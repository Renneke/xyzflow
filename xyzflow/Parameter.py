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
    def __init__(self, value:any, description:str="") -> None:
        """Parameter initialisation

        Args:
            value (any): _description_
            description (str, optional): _description_. Defaults to "".
        """
        super().__init__(cacheable=False)
        self.value = value
        self.description = description
        
        # We know already the result -> no need to run it
        self.failed = False
        self.has_run = True
        self.read_from_cache = False
        self.result = self.value
        self.execution_time = 0
                           
    def __repr__(self) -> str:
        return f"{self.description}: {self.value}"
    
