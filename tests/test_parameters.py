import shutil
from xyzflow import task, Parameter, Add, get_flow_parameter, flow, inspect_parameters, Flow, load_parameters, save_parameters
from tests import flowB
import pytest
import os

expected_result = """{
    "XB": 10,
    "YB": 10,
    "flowA.YA": 10
}"""

def test_write_read_parameters():
    
    save_parameters(flowB, "parameters.json")
    print(os.path.abspath("parameters.json"))
    assert os.path.isfile("parameters.json")
    with open("parameters.json", "r") as f:
        assert f.read() == expected_result
    
    Parameter.reset()
    assert not Parameter.parameters
    load_parameters("parameters.json")
    assert Parameter.parameters == {
                                        "XB": 10,
                                        "YB": 10,
                                        "flowA.YA": 10
                                    }
    
    