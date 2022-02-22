"""
Flows
"""
from ast import Param
from .Task import Task
from .Parameter import Parameter

def flow(flow_module, name:str, parameters=None, **kwargs)->Task:
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
    
    result = flow_module.main()
    
    Parameter.current_prefix = backup # restore old prefix
    return result
      
def get_flow_parameter(flow_module) -> dict:
    """Get the parameters of a flow.

    Args:
        flow_module (module): The flow module that you imported (e.g. import flowA).

    Returns:
        dict: Dictionary with description:default_value pairs
    """
    result = flow_module.main()
    graph = result._create_digraph()
    leaf_nodes = [node for node in graph.nodes if graph.in_degree(node)!=0 and graph.out_degree(node)==0]
    
    parameters = {n.name: n.value for n in leaf_nodes if n.__class__.__name__=="Parameter"}
    return parameters