"""
Flows
"""
from .Task import Task
from .Parameter import Parameter
import inspect
import json

class Flow:
    """Abstract class to define a Flow.
    Just override the `main()` method.
    """
    __identifier__ = "XYZFLOW"
    
    def main(self) -> Task:
        """Override this main method

        Raises:
            Exception: When not implemented

        Returns:
            Task: The result task of the flow
        """
        raise Exception("You need to override this function and let it return your resulting task.")
     
def get_task_from_flow(flow)->Task:
    """Search the main() method of a flow (can be a class or a module) and execute it. Return the result task.

    Args:
        flow (class or module): The flow

    Raises:
        Exception: If flow is not a class and not a module

    Returns:
        Task: The result task of the flow
    """
    if inspect.isclass(flow):
        return flow().main()
    elif inspect.ismodule(flow):
        return flow.main()
    
    raise Exception("First parameter has to be a module (defining a main()) or a class (defining a main())")

def save_parameters(flow, path:str):    
    """Save parameters of a flow to a file in json format

    Args:
        flow (class or module): Flow to inspect
        path (str): Path to a json file that will be overwritten
    """
    result_task = get_task_from_flow(flow)
    with open(path, "w") as f:
        json.dump(result_task.get_parameters(), f, indent=4)
    print(f"[INFO] Stored parameters of flow {flow} to {path}")
    
def load_parameters(path:str):
    """Load parameters from a json file.
    The parameters will be placed inside Parameter.parameters and are available globally.
    All parameters that will be created via `Parameter.create()` with the same name will take the values inside of this dictionary.

    Args:
        path (str): Path to a json formatted file (created via `save_parameters()`)
    """    
    with open(path, "r") as f:
        Parameter.parameters = json.load(f)
    print(f"[INFO] Restored parameters from {path}")


def flow(flow, name:str=None, parameters:dict=None, **kwargs)->Task:
    """Add another flow to this one and return its result task.
    The flow requires a `main()->Task` function that returns the result.

    Args:
        flow (module): The module or class containing a main() method
        name (str): Name of the flow. If None, parameters will not be prefixed (You should always give a name! Only if you know what you are doing, then ignore it). Default: None. 
        parameters (dict): Dictionary with parameters that shall be used (hierarchy possible because you can use . in keys)
        **kwargs (dict): Key-Value pairs with parameters to use (no hierachy possible because you cannot use . in arguments)
        
    Returns:
        Task: Resulting task
    """
    
    if not parameters:
        parameters = {}
        
    if name:
        backup = Parameter.current_prefix
        Parameter.current_prefix += name+"."    
        print(f"[INFO] Current prefix: {Parameter.current_prefix}")
        
    Parameter.setup_parameters(parameters)
    Parameter.setup_parameters(kwargs)
    
    result = get_task_from_flow(flow)
    
    if name:
        Parameter.current_prefix = backup # restore old prefix
            
    return result
      
def get_flow_parameter(flow_module_or_class) -> dict:
    """Get the parameters of a flow.

    Args:
        flow (class or module): The flow module that you imported (e.g. import flowA).

    Returns:
        dict: Dictionary with description:default_value pairs
    """               
    return flow(flow_module_or_class).get_parameters()
