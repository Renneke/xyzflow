"""
# Task Page
This is some introduction to Tasks in xyzflow.
"""

import json
from typing import Union
import networkx as nx
import threading
from diskcache import Cache
import pickle
import inspect
import time
import os
from colorama import Back, Style
from tabulate import tabulate

class Task:
    """Task

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        _type_: _description_
    """
    unique_counter = 0
    cache_location = ".xyzcache" 
    callbacks = []    
    
    global_batch_count = 0 # keep track of the batch counter
    
    def __init__(self, cacheable:bool=True, invalidator=None) -> None:
        """Task Constructor

        Args:
            cacheable (bool, optional): _description_. Defaults to True.
            invalidator (_type_, optional): _description_. Defaults to None.
        """
        self.input_unnamed : list[Task] = []
        self.input_named : dict[str, Task] = {}
        self.invalidator = invalidator
        self.cacheable = cacheable
        self.id = Task.unique_counter
        self.step = -1   
        Task.unique_counter += 1
                        
        self.log_location = os.path.join(self.cache_location, f"{self.id}-{{key}}.log")
          
        os.makedirs(self.cache_location, exist_ok=True)
        
        self.execution_time = 0
        self.in_progress = False
        self.failed = False
        self.has_run = False
        self.read_from_cache = False
                
        self.result = None
                   
    def __add__(self, other):
        import xyzflow.HelperTasks as HelperTasks
        return HelperTasks.Add(self, other)
    
    def __sub__(self, other):
        import xyzflow.HelperTasks as HelperTasks
        return HelperTasks.Sub(self, other)
                   
    def __mul__(self, other):
        import xyzflow.HelperTasks as HelperTasks
        return HelperTasks.Multiplication(self, other)

    
    @classmethod 
    def add_callback(cls, func):
        cls.callbacks.append(func)
        
    def notify(self, event:str, **kwargs):
        for func in self.callbacks:
            func(self, event, **kwargs)     
        
    @classmethod                 
    def parse_input(cls, tasks:Union[list,dict]) -> Union[list,dict]:
        
        if isinstance(tasks, dict):
            input = {}
            for name, task in tasks.items():
                if not isinstance(task, Task):
                    input[name] = Constant(task) # convert to task if it is not one
                else:
                    input[name] = task
            return input
        
        elif isinstance(tasks, list) or isinstance(tasks, tuple):
            input = []
            for task in tasks:
                if not isinstance(task, Task):
                    input.append(Constant(task)) # convert to task if it is not one
                else:
                    input.append(task)
            return input
        else:
            raise Exception("Parse inputs failed because the input argument is not a list or a dict!")
        
    def get_parameters(self) -> dict:
        """Create the current dependency graph and extract all leaf nodes of type Parameter = Parameters

        Returns:
            dict: All parameters in form of a dictionary
        """
        graph = self._create_digraph()
        leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
        return {n.name: n for n in leaf_nodes if n.__class__.__name__=="Parameter"}
                
    @property
    def all_input_tasks(self)->list[any]:
        return list(self.input_named.values()) + list(self.input_unnamed)
        
    def _create_digraph(self, graph=None):
        """Create the directed dependency graph

        Args:
            graph (networkx.graph, optional): The nx.DiGraph instance. Defaults to None.

        Returns:
            graph: The finished graph
        """
        if not graph:
            graph = nx.DiGraph()
            graph.add_node(self)
        
        # First execute all inputs and create the graph
        for input_task in self.all_input_tasks:            
            graph.add_node(input_task)            
            graph.add_edge(self, input_task)                        
            input_task._create_digraph(graph=graph)
        return graph
                    
    def visualize(self):                     
        graph = self._create_digraph() # pragma: no cover
        color_map = ['blue' if node == self else 'green' for node in graph]     # pragma: no cover
        nx.draw(graph, with_labels=True, font_weight='bold', node_color=color_map) # pragma: no cover
        
        import matplotlib.pyplot as plt # pragma: no cover
        plt.show() # pragma: no cover
        
    def status(self):    
        """Render a table of the current status of this task and its parents
        """
        graph = self._create_digraph()
        
        def addColumn(node, column):
            if node.failed:
                column += [f"{Back.RED} {node.id}) {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
            elif node.read_from_cache:
                column += [f"{Back.CYAN} {node.id}) {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
            elif node.has_run:
                column += [f"{Back.GREEN} {node.id}) {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
            else:
                column += [f"{Back.YELLOW} {Style.BRIGHT} {node.id})  {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
        
        table = []
        
        for steps in range(0, len(graph)):
            leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
            
            column = []
            for node in leaf_nodes:
                addColumn(node, column)
            graph.remove_nodes_from(leaf_nodes)
            if column:
                table += [column]
        
        column = []
        addColumn(self, column)
        table += [column]
        
        import pandas as pd
        df = pd.DataFrame(table).T
        print(tabulate(df,showindex=False,headers=[f"Step {i}" for i in range(0, len(df.columns))]))
            
    def _calc_hash(self):
        obj = []
        for input in self.all_input_tasks:
            obj.append(input.__class__.__name__)
            obj.append(input.result)
        return f"{self.__class__.__name__}_{pickle.dumps(obj)}_{inspect.getsource(self.run)}"
        
        
    def _run(self, *args, **kwargs):
        """Run the flow

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        self.notify("start")
        if self.has_run:
            self.notify("finished")
            return # no need to run it again if it already has run
        
        start = time.time()
        
        # First check if input data is valid
        for task in self.all_input_tasks:
            if not task.has_run: # pragma: no cover
                raise Exception(f"The task {task} has not been run but it is an input to {self}. This should never happen! BUG found!") # pragma: no cover
            if task.failed:
                self.failed = True
                self.has_run = True
                self.read_from_cache = False
                self.notify("failed")
                return
        
        with open(self.log_location.replace("{key}", "xyzflow"), "w") as log:
            with Cache(self.cache_location) as cache:
                        
                self.key = self._calc_hash() # unique hash that contains run source code, class name and input state
                self.notify("key")
                        
                log.write(f"[INFO] Start execution of {self} at {start}\n")
                    
                # check if task is already in the cache
                self.read_from_cache = True
                if not self.cacheable:
                    self.read_from_cache = False
                if self.key not in cache:
                    self.read_from_cache = False
                if self.invalidator and self.invalidator():
                    self.read_from_cache = False
                    log.write(f"[INFO] {self.__class__.__name__} - Invalidator returned True: Do not use the cache!\n")
                                    
                if self.read_from_cache:
                    data = cache.get(self.key)
                    
                    self.result = data["result"]
                    self.failed = False
                    self.has_run = True
                    log.write(f"[INFO] {self.__class__.__name__}: {self} is read from cache: Result {self.result}\n")
                    self.execution_time = time.time() - start
                    self.notify("cached")
                    return
                
            
                log.write(f"[INFO] {self.__class__.__name__}: {self} not using cache because no suitable entry found\n")                                    
                log.write(f"[INFO] {self.__class__.__name__}: {self} starts\n")   
                self.in_progress = True
                try:
                    self.result = self.run(*args, logger=log, **kwargs)
                    self.notify("success")
                    
                    self.failed = False
                    if self.cacheable:
                        cache.set(self.key, {
                            "result": self.result
                        })
                        log.write(f"[INFO] {self.__class__.__name__}: {self} Result has been written to the cache\n")  
                except Exception as e:
                    self.failed = True
                    log.write(f"[ERROR] Exception occured in {self}: {e}\n") 
                    self.notify("failed")
                self.in_progress = False
                self.has_run = True                
                log.write(f"[INFO] {self.__class__.__name__}: {self} finished\n") 
    
            self.execution_time = time.time() - start      
            self.notify("exec_time")
                
            
    def __call__(self, *args: any, **kwargs: any) -> any:
        """Call operator

        Returns:
            any: _description_
        """
                                 
        graph = self._create_digraph()
                          
        # Go through the graph layer by layer
        # Each layer can be started in "parallel" (in multiple threads)
        # because they are independent
        for step in range(0, len(graph)):
            leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
            
            queue = []
            for i, node in enumerate(leaf_nodes):
                node.step = step
                thread = threading.Thread(target=node._run)
                thread.start()
                queue += [thread]
            for thread in queue:
                thread.join()
            
            # Dump out batch information
            with open(os.path.join(self.cache_location, f"{Task.global_batch_count}-batch.json"), "wb") as f:
                pickle.dump(leaf_nodes, f)
            Task.global_batch_count += 1
                      
            graph.remove_nodes_from(leaf_nodes)
            
        # Last but not least run the root node
        self.step = step+1
        self._run(*args, **kwargs)               
        
        return self.result
        
    def run(self, *args: any, **kwargs: any):
        """Run method (to be overwritten by tasks)

        Raises:
            Exception: _description_
        """
        raise Exception(f"No run method has been implemented for {self.__class__.__name__}.") # pragma: no cover


class Constant(Task):
    """Constant

    Args:
        Task (_type_): _description_
    """
    def __init__(self, value:any) -> None:
        super().__init__(cacheable=False)

        self.failed = False        
        self.result = value
            
        # We know already the result -> no need to run it
        self.has_run = True
        self.read_from_cache = False
        self.execution_time = 0
        
    def __repr__(self) -> str:
        return f"{self.result}"
    
    
    
    

def task(cacheable=True):
    """Task decorator

    Args:
        cacheable (bool, optional): Is this task cacheable? Defaults to True.
    """
    
    def inner(func):
        taskname = func.__name__
        
        class WrapperTask(Task):
            def __init__(self, cacheable, *args, **kwargs) -> None:
                super().__init__(cacheable)
                self.input_unnamed = self.parse_input(args)
                self.input_named = self.parse_input(kwargs)
                
            def __repr__(self) -> str:
                return f"{taskname}"
                
            def get_inputs(self):
                args = [v.result for v in self.input_unnamed]
                kwargs = {name: v.result for name, v in self.input_named.items()}
                return args, kwargs
                
            def run(self, *args: any, **kwargs: any):
                list_input, dict_input = self.get_inputs()
                
                args_signiture = inspect.signature(func)
                
                to_be_deleted = [k for k in kwargs.keys() if k not in args_signiture.parameters]
                for key in to_be_deleted:
                    kwargs.pop(key)
                    
                return func(*list_input, *args, **dict_input, **kwargs)
    
        def factory(*args, **kwargs):
            return WrapperTask(cacheable, *args, **kwargs)
    
        return factory
    
    return inner
    