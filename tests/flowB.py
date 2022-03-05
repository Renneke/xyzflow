from xyzflow import Parameter, flow, Flow, Task

from tests import flowA
  
class FlowC(Flow):
    """Example FlowC
    """
    def main(self) -> Task:
        x = Parameter.create(value=11, name="XC", description="X from Flow C")
        y = Parameter.create(value=12, name="YC")   
        return x+y
  
def main():
    # Define parameters
    x = Parameter.create(value=10, name="XB", description="X from Flow B")
    y = Parameter.create(value=10, name="YB")    
    z = x + y + flow(flowA, "flowA", XA=x)
    return z
       
if __name__ == "__main__":   
    print(main()()) # Execute flow and print the result
  