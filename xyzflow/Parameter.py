"""
# Parameter Page
This is some introduction to Parameters in xyzflow.
"""
from ast import Param
from .Task import Task
import inspect


class Parameter(Task):
    """
    # Parameter Task
    
    A parameter is always a leaf node of the dependency graph.
    In the flow, the user can set these parameters.
    A Parameter has a default value and a description.
    It can take any type.
    A Parameter task is not executed because no calculation has to be done.
    It cannot be cached. Therefore, the execution time is always 0s.

    Args:
        Task (_type_): _description_
    """
    
    current_prefix = ""
    parameters = {} # Global storage of parameters
    
    @classmethod
    def reset(cls):
        cls.parameters.clear()
        cls.current_prefix = ""
        
    @classmethod
    def setup_parameters(cls, parameters):
        """Append the current prefix and add the parameters to the global scope

        Args:
            parameters (_type_): _description_
        """
        cls.parameters.update({Parameter.current_prefix+k:v for k,v in Task.parse_input(parameters).items()})
        
    def __init__(self, name:str, value:any, description:str="") -> None:
        super().__init__(cacheable=False)
        
        self.name = name
        self.description = description
        
        # We know already the result -> no need to run it
        self.value = value
        self.failed = False
        self.has_run = True
        self.read_from_cache = False
        self.result = self.value
        self.execution_time = 0
               
        
    @classmethod    
    def create(cls, name:str, value:any, description:str=""):        
        """
        Parameter factory. Must be used to support hierarchy
        """            
        name = Parameter.current_prefix + name
        if name in Parameter.parameters:
            para = Parameter.parameters[name] # completly replace this instance!
            return para # nothing to anymore
        else:
            Parameter.parameters[name] = Parameter(name, value, description=description)
                
        return Parameter.parameters[name]
                               
    def __repr__(self) -> str:
        return f"{self.name}: {self.value}"
    
