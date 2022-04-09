import shutil
from xyzflow import task, Parameter, Add, get_flow_parameter, flow, inspect_parameters, Flow, load_parameters, save_parameters
from tests import flowB
import pytest
import os

expected_result = """{
    "XB": {
        "name": "XB",
        "description": "X from Flow B",
        "value": 10
    },
    "YB": {
        "name": "YB",
        "description": "",
        "value": 10
    },
    "flowA.YA": {
        "name": "flowA.YA",
        "description": "",
        "value": 10
    }
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
    assert {k:v.to_dict() for k,v in Parameter.parameters.items()} == {
    "XB": {
        "name": "XB",
        "description": "X from Flow B",
        "value": 10
    },
    "YB": {
        "name": "YB",
        "description": "",
        "value": 10
    },
    "flowA.YA": {
        "name": "flowA.YA",
        "description": "",
        "value": 10
    }
}
    
    