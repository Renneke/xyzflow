from xyzflow import Parameter, flow, Flow, Task
import logging
from tests import flowA
  
logger = logging.getLogger('flowC')
class FlowC(Flow):
    """Example FlowC
    """
    def main(self) -> Task:
        x = Parameter.create(value=11, name="XC", description="X from Flow C")
        y = Parameter.create(value=12, name="YC")   
        z = flow(flowA, "I1", XA=y)
        logger.info("Hello World")
        return x-y*z+10