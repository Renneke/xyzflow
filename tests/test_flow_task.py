import shutil
from xyzflow import task, Parameter, Add, get_flow_parameter, flow, inspect_parameters, Flow, Task
from xyzflow.Flow import get_task_from_flow
from tests import flowA
import pytest

def test_module_flow():
    Parameter.reset()
    xy = Parameter.create(name="a", value=100)

    b = flow(flowA, name="I1", parameters={"XA": xy})

    b = Add(b, xy)

    assert b() == 210
    
def test_exception():
    # You have to override the function
    with pytest.raises(Exception):
        Flow().main()
        
    
    with pytest.raises(Exception):
        Task.parse_input("not working")
        
    with pytest.raises(Exception):
        get_task_from_flow("not working")

def test_flow():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    a = Parameter(value=1, name="a")
    result_of_flowA = flow(flowA, "flowA", XA=a)
    assert result_of_flowA() == 11
    assert list(get_flow_parameter(flowA).keys()) == ["XA", "YA"]
    
    assert str(inspect_parameters("tests/flowA.py")) == "{'XA': 10, 'YA': 10}"
        
        
class MyFlow(Flow):
    def main(self):
        a = Parameter.create("a", 10)
        b = Parameter.create("b", 20)
        return a+b
    
    
def test_class_flow():
    Parameter.reset()
    a = flow(MyFlow, "I1", b=11)
    assert a() == 21