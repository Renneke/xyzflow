"""
# Parameter Page
This is some introduction to Parameters in xyzflow.
"""
from .Task import Task


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
    parameters = {} # Global storage of parameters str->Parameter/Task
    
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
        
        self.name = name
        self.description = description
        self.value = value
        
        super().__init__(cacheable=False)
        
        # We know already the result -> no need to run it
        self.failed = False
        self.has_run = True
        self.read_from_cache = False
        self._result = self.value
        self.execution_time = 0
        
    def set(self, value):
        self.value = value
        self._result = value        
               
    def to_dict(self)->dict:
        """Convert this parameter to a dictionary so that it can be stored

        Returns:
            dict: Dictionary with all important stuff
        """
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value
        }
        
    @classmethod    
    def create(cls, name:str, value:any, description:str=""):        
        """
        Parameter factory. Must be used to support hierarchy
        """            
        name = Parameter.current_prefix + name
        
        if name in Parameter.parameters:
            return Parameter.parameters[name]
                        
        Parameter.parameters[name] = Parameter(name, value, description=description)
        return Parameter.parameters[name]
                               
    def __repr__(self) -> str:
        return f"<Parameter: {self.name}: {self.value}>"
    
