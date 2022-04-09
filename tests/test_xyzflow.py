import sys
from xyzflow import Parameter, Add, Task, flow, get_flow_parameter, inspect_parameters, Sub, main
import pytest
import shutil
import tests.flowA as flowA
import subprocess

class SimpleTask(Task):
    def __init__(self) -> None:
        super().__init__(invalidator=self.invalidator)
        
    def invalidator(self):
        return True
        
    def run(self, *args: any, **kwargs: any):
        print("Hallo")

def test_invalidator():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    x = SimpleTask()
    x()
    assert x.read_from_cache == False
    x.has_run = False
    x() # Simple task gets invalidated all the time!
    assert x.read_from_cache == False
    
    x.cacheable = False
    x.invalidator = None
    x.has_run = False
    x()
    assert x.read_from_cache == False
    x.has_run = False
    x()
    assert x.read_from_cache == False # now it should not be cacheable
    
    
def test_add():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    a = Parameter(value=1, name="1")
    b = Parameter(value=2, name="2")
    c = a+b
    assert c() == 3
    
def test_evaluated_value():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    a = Parameter(value=1, name="1")
    b = Parameter(value=2, name="2")
    c = a*b
    c.status()
    d = Add(c(), 4)
    d -= 5
    assert d() == 1
    d.status()
    d.has_run = False # invalidate task
    d()
    d.status()
    assert d.read_from_cache == True
    
    x = Sub()
    y = x()
    assert x.failed == True
    
    
def test_error_in_task():
    Parameter.reset()
    shutil.rmtree(".xyzcache", ignore_errors=True)
    x = Add(1, "STRING") # Can't be added    
    a = x()
    
    assert a == None
    assert x.failed == True
    assert x.has_run == True
    
    x.status()
    b = x + x
    b()
    assert b.failed == True
    assert b.has_run == True
    b.status()
    
def test_cli(capsys):
    Parameter.reset()
    subprocess.check_output("xyzflow --help", shell=True)
    
    sys.argv = ["", "parameters", "tests/flowA.py"]
    main()
    assert "{'XA': 10, 'YA': 10}" in capsys.readouterr().out.strip()
    