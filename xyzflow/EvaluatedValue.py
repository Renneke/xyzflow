from .Task import Task

class EvaluatedValue(Task):
    """Evaluated Value Task

    Args:
        Task (_type_): _description_
    """
    def __init__(self, value:any, parent_task:Task=None) -> None:
        super().__init__(cacheable=False)

        self.failed = False
        
        self.result = value
        if parent_task:
            self.input_named = {
                "__do_not_execute": parent_task
            }           
            self.failed = parent_task.failed   # take over status of parent task  
        
            
        # We know already the result -> no need to run it
        self.has_run = True
        self.read_from_cache = False
        self.execution_time = 0
        
    def __repr__(self) -> str:
        return f"{self.result}"
        