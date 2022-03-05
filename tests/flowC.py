from xyzflow import Parameter, flow, Flow, Task

from tests import flowA
  
class FlowC(Flow):
    """Example FlowC
    """
    def main(self) -> Task:
        x = Parameter.create(value=11, name="XC", description="X from Flow C")
        y = Parameter.create(value=12, name="YC")   
        z = flow(flowA, "I1", XA=y)
        
        return x-y*z+10