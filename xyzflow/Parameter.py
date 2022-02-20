from .Task import Task


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
               
            
    def __repr__(self) -> str:
        return f"{self.description}: {self.value}"
    
