"""
Flows
"""
from .Task import Task

def flow(flow_module, **kwargs)->Task:
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
    for k,v in kwargs.items():
        if k not in dir(flow_module):
            raise Exception(f"Parameter {k} not found in {flow_module}")
        if not isinstance(getattr(flow_module, k), Task):
            raise Exception(f"You want to set {k} in {flow_module}, but that one is not a task!")
        setattr(flow_module, k, v) # Replace parameter with input task
            
    return flow_module.main()
      
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
    
    parameters = {n.description: n.value for n in leaf_nodes if n.__class__.__name__=="Parameter"}
    return parameters