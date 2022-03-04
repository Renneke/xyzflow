from xyzflow import Parameter, flow

from tests import flowA
  
def main():
    # Define parameters
    x = Parameter.create(value=10, name="XB")
    y = Parameter.create(value=10, name="YB")    
    z = x + y + flow(flowA, "flowA", XA=x)
    return z
       
if __name__ == "__main__":   
    print(main()()) # Execute flow and print the result
  