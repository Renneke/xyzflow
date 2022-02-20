from typing import Union
from .Task import Task


class Add(Task):
    """Addition Task

    Args:
        Task (_type_): _description_
    """
    def __init__(self, *args:list[Union[Task,int,float]]) -> None:
        """Initializing an addition task
        """
        super().__init__(cacheable=True)        
        self.input_unnamed = self.parse_input(args)
            
    def run(self, *args: any, **kwargs: any):
        sum = 0
        for input in self.all_input_tasks:
            sum += input.result  
        return sum

class Sub(Task):
    """Subtraction Task

    Args:
        Task (_type_): _description_
    """
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
    """Multiplication Task

    Args:
        Task (_type_): _description_
    """
    def __init__(self, *args:list[Union[Task,int,float]]) -> None:
        super().__init__(cacheable=True)        
        self.input_unnamed = self.parse_input(args)
            
    def run(self, *args: any, **kwargs: any):
        mult = 1
        for input in self.all_input_tasks:
            mult *= input.result  
        return mult