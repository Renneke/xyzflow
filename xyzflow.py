from ctypes import Union
import logging
import networkx as nx
import matplotlib.pyplot as plt
import threading
from diskcache import Cache
import pickle
import inspect
import time


logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

        
class Task:
        
    def __init__(self, cache_location=".xyzcache", cacheable:bool=True) -> None:
        self.input_unnamed : list[Task] = []
        self.input_named : dict[str, Task] = {}
        self.invalidator = None
        self.cacheable = cacheable
                
        self.cache_location = cache_location
          
        self.execution_time = 0
        self.in_progress = False
        self.failed = False
        self.has_run = False
        self.read_from_cache = False
                
        self.result = None
        self.logs = ""
                
    @property
    def all_input_tasks(self):
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
                column += [f"{Back.RED} {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
            elif node.has_run:
                column += [f"{Back.GREEN} {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
            else:
                column += [f"{Back.YELLOW} {Style.BRIGHT} {node.__class__.__name__}: {node} {Style.RESET_ALL} {node.execution_time*1e3:.1f} ms"]
        
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
        
    def _compare_inputs(self, cached_inputs):
        # Call invalidator -> If the callback returns True, then we return False to force
        # rerunning the task
        if self.invalidator and self.invalidator():
            print("[INFO] Invalidator says it is not valid!")
            return False
        
        # An input is the same if the class is the same and the result is the same
        for i, input in enumerate(self.all_input_tasks):
            cached_input = cached_inputs[i]
            if input.__class__ != cached_input.__class__:
                print(f"[INFO] Class not the same: {input.__class__}!={cached_input.__class__}")
                return False
            # Serialize it so that we can compare them
            if pickle.dumps(input.result) != pickle.dumps(cached_input.result):
                print("[INFO] Input not the same")
                return False
        
        return True # they match
        
    def _calc_hash(self):
        obj = []
        for input in self.all_input_tasks:
            obj.append(input.__class__.__name__)
            obj.append(input.result)
        return f"{self.__class__.__name__}_{pickle.dumps(obj)}_{inspect.getsource(self.run)}"
        
    def _run(self, *args, **kwargs):
        """Execution of the run method
        """
        start = time.time()
        
        # First check if input data is valid
        for task in self.all_input_tasks:
            if not task.has_run:
                raise Exception("NOPE!")
            if task.failed:
                self.failed = True
                self.has_run = True
                self.read_from_cache = False
                return
        
        with Cache(self.cache_location) as cache:
                    
            key = self._calc_hash() # unique hash that contains run source code, class name and input state
                    
            # check if task is already in the cache
            if self.cacheable and key in cache:
                data = cache.get(key)
                  
                self.result = data["result"]
                self.failed = False
                self.has_run = True
                self.read_from_cache = True
                self.logs += f"[INFO] {self.__class__.__name__}: {self} is read from cache: Result {self.result}\n"
                logging.info(self.logs)     
                self.execution_time = time.time() - start
                return
            
            self.logs += f"[INFO] {self.__class__.__name__}: {self} not using cache because no suitable entry found\n"        
            self.read_from_cache = False
            
            self.logs += f"[INFO] {self.__class__.__name__}: {self} starts\n"
            self.in_progress = True
            try:
                self.result = self.run(*args, **kwargs)
                self.failed = False
                if self.cacheable:
                    cache.set(key, {
                        "result": self.result,
                        "inputs": self.all_input_tasks
                    })
                    self.logs += f"[INFO] {self.__class__.__name__}: {self} Result has been written to the cache\n" 
            except Exception as e:
                self.failed = True
                self.logs += f"[ERROR] Exception occured in {self}: {e}\n"
            self.in_progress = False
            self.has_run = True
            self.logs += f"[INFO] {self.__class__.__name__}: {self} finished\n" 

        logging.info(self.logs)       
        self.execution_time = time.time() - start      
             
            
    def __call__(self, *args: any, **kwargs: any) -> any:
        
        # Get execution_queue from parent caller
        execution_queue = []                                    
        graph = self._create_digraph()
        self._call(execution_queue=execution_queue)
                          
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
        
        return self.result
        
    def run(self, *args: any, **kwargs: any):
        raise Exception(f"No run method has been implemented for {self.__class__.__name__}.")


class Parameter(Task):
    def __init__(self, name:str, value:any, description:str="") -> None:
        self.name = name
        self.value = value
        self.description = description
        super().__init__(cacheable=False)
        
    def run(self, *args: any, **kwargs: any):
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.name} = {self.value}"
    
class Add(Task):
    def __init__(self, *args:list[Task]) -> None:
        super().__init__()        
        self.input_unnamed = args
            
    def run(self, *args: any, **kwargs: any):
        sum = 0
        for input in self.input_unnamed:
            sum += input.result            
        if sum==35:
            time.sleep(0.5)
        return sum
  
  
if __name__ == "__main__":   
           
    x = Parameter(name="a", value=10, description="Var A")
    y = Parameter(name="b", value=25, description="Var B")
    e10 = Add(x, y)
    e11 = Add(x, y)
    e2 = Add(e10, e11)
    e3 = Add(e10, e2)
    
    e11()
    e3.status()
    
    e2()
    e3.status()
    
    print(e3())
    e3.status()
    
    e3.visualize()
