import argparse
import importlib.util
from pprint import pprint
from .Flow import get_flow_parameter, Flow
import sys
import inspect
import os

def load_flow_from_file(path:str):
    """Load a flow from a python file.
    The file has to be either a main() function or a class inheriting from `Flow`.

    Args:
        path (str): Path to the python file

    Raises:
        Exception: No main() method found

    Returns:
        module/instance: Module or instance that contains the main() function.
    """    
    
    spec = importlib.util.spec_from_file_location("flow", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, "main") and inspect.isfunction(module.main):
        return module
    
    for k, v in module.__dict__.items():
        if hasattr(v, "__identifier__") and v.__identifier__=="XYZFLOW" and v.__module__!="xyzflow.Flow":
            return v()

    raise Exception(f"There is no main() method or Flow defined in the python file: {path}!")
    
    
      
def inspect_parameters(path_or_module:str)->dict:    
    """Get the parameters of a flow from a path or a module.
    This function can be directly called from the cli program.

    Args:
        path_or_module (str): Path to a python file containing a flow or a python module that contains a flow

    Returns:
        dict: Dictionary containing the parameters
    """
    if os.path.isfile(path_or_module):
        module = load_flow_from_file(path_or_module)
    else:
        module = __import__(path_or_module)
        
    parameters = get_flow_parameter(module)
    pprint(parameters)
    return parameters
    
    
def main(): 
    parser = argparse.ArgumentParser(description='XYZflow cli tool')
    
    subparsers = parser.add_subparsers(help='commands')
    parser_parameters = subparsers.add_parser('parameters', help='Inspect a flow and print out all input parameters')
    parser_parameters.add_argument('py', help='Python file or installed module containing the flow (must have a main())')
    parser_parameters.set_defaults(func=inspect_parameters)
        
    args = parser.parse_args(sys.argv[1:])
    args.func(args.py)