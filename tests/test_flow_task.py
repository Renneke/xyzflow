import shutil
from xyzflow import task, Parameter, Add, get_flow_parameter, flow, inspect_parameters, Flow
from tests import flowA
import pytest

def test_module_flow():
    Parameter.reset()
    xy = Parameter.create(name="a", value=100)

    b = flow(flowA, name="I1", parameters={"XA": xy})

    b = Add(b, xy)

    assert b().result == 210
    

def test_flow():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    a = Parameter(value=1, name="a")
    result_of_flowA = flow(flowA, "flowA", XA=a)
    assert result_of_flowA().result == 11
    assert get_flow_parameter(flowA) == {"XA": 10, "YA": 10}
    
    class dummy_args:
        py = "tests/flowA.py"
    
    
    assert inspect_parameters(dummy_args) == {"XA": 10, "YA": 10}
    
    with pytest.raises(Exception):
        flow(flowA, l=10)
    
    with pytest.raises(Exception):
        flow(flowA, __file__=10)
        
class MyFlow(Flow):
    def main(self):
        a = Parameter.create("a", 10)
        b = Parameter.create("b", 20)
        return a+b
    
    
def test_class_flow():
    Parameter.reset()
    a = flow(MyFlow, "I1", b=11)
    assert a().result == 21