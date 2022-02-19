from typing import Union
from unittest import TextTestRunner
import networkx as nx
import matplotlib.pyplot as plt
import threading
from diskcache import Cache
import pickle
import inspect
import time
import os
import argparse
import importlib.util
from pprint import pprint
        
class Task:
    
    unique_counter = 0
    
    def __init__(self, cache_location=".xyzcache", cacheable:bool=True) -> None:
        self.input_unnamed : list[Task] = []
        self.input_named : dict[str, Task] = {}
        self.invalidator = None
        self.cacheable = cacheable
        self.id = Task.unique_counter
        Task.unique_counter += 1
        
                
        self.cache_location = cache_location
        self.log_location = os.path.join(cache_location, f"{self.id}-{{key}}.log")
          
        os.makedirs(self.cache_location, exist_ok=TextTestRunner)
        # remove all existing logs for this task number
        os.system(f"rm -rf \"{ self.log_location.replace('{key}', '*') }\"")
        
        self.execution_time = 0
        self.in_progress = False
        self.failed = False
        self.has_run = False
        self.read_from_cache = False
                
        self.result = None
                   
    def __add__(self, other):
        return Add(self, other)
    
    def __sub__(self, other):
        return Sub(self, other)
                   
    def __mul__(self, other):
        return Multiplication(self, other)
                
    def _is_evaluated_task(self, var):
        return isinstance(var, tuple) and len(var)==2 and isinstance(var[1], Task)
                
    def parse_input(self, tasks:list):
        input = []
        for task in tasks:
            if not isinstance(task, Task):
                input.append(EvaluatedValue(task)) # convert to task if it is not one
            else:
                input.append(task)
        return input
                
    @property
    def all_input_tasks(self)->list[any]:
        return list(self.input_named.values()) + list(self.input_unnamed)
        
    def _create_digraph(self, graph=None):
        if not graph:
            graph = nx.DiGraph()
            graph.add_node(self)
        
        # First execute all inputs and create the graph
        for input_task in self.all_input_tasks:            
            graph.add_node(input_task)            
            graph.add_edge(self, input_task)                        
            input_task._create_digraph(graph=graph)
        return graph
            
    def _call(self, execution_queue):
        for input_task in self.all_input_tasks:                                  
            input_task._call(execution_queue=execution_queue)
        
    def visualize(self):                     
        graph = self._create_digraph()
        color_map = ['blue' if node == self else 'green' for node in graph]    
        nx.draw(graph, with_labels=True, font_weight='bold', node_color=color_map)
        plt.show()
        
    def status(self):    
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
            
            from colorama import Back, Style, Fore
            column = []
            for node in leaf_nodes:
                addColumn(node, column)
            graph.remove_nodes_from(leaf_nodes)
            if column:
                table += [column]
        
        column = []
        addColumn(self, column)
        table += [column]
        
        from tabulate import tabulate
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
        """Execution of the run method
        """
        if self.has_run:
            return # no need to run it again if it already has run
        
        start = time.time()
        
        # First check if input data is valid
        for task in self.all_input_tasks:
            if not task.has_run:
                raise Exception(f"The task {task} has not been run but it is an input to {self}. This should never happen! BUG found!")
            if task.failed:
                self.failed = True
                self.has_run = True
                self.read_from_cache = False
                return
        
        with open(self.log_location.replace("{key}", "xyzflow"), "w") as log:
            with Cache(self.cache_location) as cache:
                        
                key = self._calc_hash() # unique hash that contains run source code, class name and input state
                        
                log.write(f"[INFO] Start execution of {self} at {start}\n")
                    
                # check if task is already in the cache
                if self.cacheable and key in cache:
                    data = cache.get(key)
                    
                    self.result = data["result"]
                    self.failed = False
                    self.has_run = True
                    self.read_from_cache = True
                    log.write(f"[INFO] {self.__class__.__name__}: {self} is read from cache: Result {self.result}\n")
                    self.execution_time = time.time() - start
                    return
                
                log.write(f"[INFO] {self.__class__.__name__}: {self} not using cache because no suitable entry found\n")    
                self.read_from_cache = False
                
                log.write(f"[INFO] {self.__class__.__name__}: {self} starts\n")   
                self.in_progress = True
                try:
                    self.result = self.run(*args, logger=log, **kwargs)
                    
                    self.failed = False
                    if self.cacheable:
                        cache.set(key, {
                            "result": self.result,
                            "inputs": self.all_input_tasks
                        })
                        log.write(f"[INFO] {self.__class__.__name__}: {self} Result has been written to the cache\n")  
                except Exception as e:
                    self.failed = True
                    log.write(f"[ERROR] Exception occured in {self}: {e}\n") 
                self.in_progress = False
                self.has_run = True                
                log.write(f"[INFO] {self.__class__.__name__}: {self} finished\n") 
    
            self.execution_time = time.time() - start      
                
            
    def __call__(self, *args: any, **kwargs: any) -> any:
                                 
        graph = self._create_digraph()
                          
        # Go through the graph layer by layer
        # Each layer can be started in "parallel" (in multiple threads)
        # because they are independent
        for steps in range(0, len(graph)):
            leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
            
            queue = []
            for node in leaf_nodes:
                thread = threading.Thread(target=node._run)
                thread.start()
                queue += [thread]
            for thread in queue:
                thread.join()
            graph.remove_nodes_from(leaf_nodes)
                      
        # Last but not least run the root node
        self._run(*args, **kwargs)               
        
        return EvaluatedValue(self.result, self)
        
    def run(self, *args: any, **kwargs: any):
        raise Exception(f"No run method has been implemented for {self.__class__.__name__}.")


    
class Parameter(Task):
    def __init__(self, value:any, description:str="") -> None:
        super().__init__(cacheable=False)
        self.value = value
        self.description = description
        
        # We know already the result -> no need to run it
        self.failed = False
        self.has_run = True
        self.read_from_cache = False
        self.result = self.value
        self.execution_time = 0
        
    def run(self, *args: any, **kwargs: any):
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.description}: {self.value}"
    

class EvaluatedValue(Task):
    def __init__(self, value:any, parent_task:Task=None) -> None:
        super().__init__(cacheable=False)

        if parent_task:
            self.input_named = {
                "__do_not_execute": parent_task
            }                
        self.result = value
            
            
        # We know already the result -> no need to run it
        self.failed = False
        self.has_run = True
        self.read_from_cache = False
        self.execution_time = 0
    
    def run(self, *args: any, **kwargs: any):
        return self.result
    
    def __repr__(self) -> str:
        return f"{self.result}"
        
class Add(Task):
    def __init__(self, *args:list[Union[Task,int,float]]) -> None:
        super().__init__(cacheable=True)        
        self.input_unnamed = self.parse_input(args)
            
    def run(self, *args: any, **kwargs: any):
        sum = 0
        for input in self.all_input_tasks:
            sum += input.result  
        return sum

class Sub(Task):
    def __init__(self, *args:list[Union[Task,int,float]]) -> None:
        super().__init__(cacheable=True)        
        self.input_unnamed = self.parse_input(args)
            
    def run(self, *args: any, logger, **kwargs: any):
        if len(self.all_input_tasks)<1:
            raise Exception("Not enough operators for substraction")
        sum = self.all_input_tasks[0].result
        for input in self.all_input_tasks[1:]:
            sum -= input.result  
        logger.write("[INFO] Subtraction ok\n")
        return sum
    
class Multiplication(Task):
    def __init__(self, *args:list[Union[Task,int,float]]) -> None:
        super().__init__(cacheable=True)        
        self.input_unnamed = self.parse_input(args)
            
    def run(self, *args: any, **kwargs: any):
        mult = 1
        for input in self.all_input_tasks:
            mult *= input.result  
        return mult
    
    
def flow(flow_module, **kwargs)->Task:
    """Add another flow to this one and return its result task.
    The flow_module requires a `main()->Task` function that returns the result.
    Parameters have to be defined on the top level.

    Args:
        flow_module (module): The module containing the flow to import

    Raises:
        Exception: If one of the parameters are not found in the module
        Exception: If the parameter to set is not a `Task`

    Returns:
        Task: _description_
    """
    for k,v in kwargs.items():
        if k not in dir(flow_module):
            raise Exception(f"Parameter {k} not found in {flow_module}")
        if not isinstance(getattr(flow_module, k), Task):
            raise Exception(f"You want to set {k} in {flow_module}, but that one is not a task!")
        setattr(flow_module, k, v) # Replace parameter with input task
            
    return flow_module.main()
      
def inspect_parameters(args):
    
    spec = importlib.util.spec_from_file_location("flow", args.py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    result = module.main()
    graph = result._create_digraph()
    leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
    
    parameters = {n.description: n.value for n in leaf_nodes if n.__class__.__name__=="Parameter"}
    
    pprint(parameters)
    
    
if __name__ == "__main__":   
    parser = argparse.ArgumentParser(description='XYZflow cli tool')
    
    subparsers = parser.add_subparsers(help='commands')
    parser_parameters = subparsers.add_parser('parameters', help='Inspect a flow and print out all input parameters')
    parser_parameters.add_argument('py', help='Python file containing the flow (must have a main())')
    parser_parameters.set_defaults(func=inspect_parameters)
    
    args = parser.parse_args()
    args.func(args)