"""
Flows
"""
from ast import Param
from .Task import Task
from .Parameter import Parameter
import inspect
import pickle
import os
class Flow:
    def main():
        raise Exception("You need to override this function and let it return your resulting task.")
    
def get_parameter_file_location(flow):
    return f"{flow.__name__}.json"    

def create_parameters(flow, result_task):
    path = get_parameter_file_location(flow)
    with open(path, "wb") as f:
        pickle.dump(result_task.get_parameters(), f)
    print(f"[INFO] Stored parameters of flow {flow} to {path}")
    
def load_parameters(flow):
    path = get_parameter_file_location(flow)
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        Parameter.parameters = pickle.load(f)
    print(f"[INFO] Restored parameters of {flow} from {path}")
    return True

def flow(flow, name:str, parameters=None, **kwargs)->Task:
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
    
    if not parameters:
        parameters = {}
        
    backup = Parameter.current_prefix
    Parameter.current_prefix += name+"."
    
    print(f"[INFO] Current prefix: {Parameter.current_prefix}")
    Parameter.setup_parameters(parameters)
    Parameter.setup_parameters(kwargs)
    
    if inspect.isclass(flow):
        result = flow().main()
    elif inspect.ismodule(flow):
        result = flow.main()
    else:
        raise Exception("First parameter has to be a module (defining a main()) or a class (defining a main())")
    
    Parameter.current_prefix = backup # restore old prefix
    
    # Store the parameters if the run was successfull
    if not result.failed:
        create_parameters(flow, result)
        
    return result
      
def get_flow_parameter(flow) -> dict:
    """Get the parameters of a flow.

    Args:
        flow (class or module): The flow module that you imported (e.g. import flowA).

    Returns:
        dict: Dictionary with description:default_value pairs
    """
        
    if inspect.isclass(flow):
        result = flow().main()
    elif inspect.ismodule(flow):
        result = flow.main()
    else:
        raise Exception("First parameter has to be a module (defining a main()) or a class (defining a main())")
        
    # Store the parameters if the run was successfull
    if not result.failed:
        create_parameters(flow, result)
        
    return result.get_parameters()
