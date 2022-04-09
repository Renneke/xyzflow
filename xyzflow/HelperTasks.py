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
        sum = None
        for input in self.all_input_tasks:
            if sum is None:
                sum = input.result
            else:
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
        mult = None
        for input in self.all_input_tasks:
            if mult is None:
                mult = input.result
            else:
                mult *= input.result  
        return mult