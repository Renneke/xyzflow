[![PyPI version](https://badge.fury.io/py/xyzflow.svg)](https://badge.fury.io/py/xyzflow) [![Total alerts](https://img.shields.io/lgtm/alerts/g/Renneke/xyzflow.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Renneke/xyzflow/alerts/)

# XYZFlow
Powerful but simple orchestration framework for python.

## Documentation

You find the latest documentation on readthedocs.io: https://xyzflow.readthedocs.io/en/latest/.
## Installing

``` bash
pip install xyzflow
```

## Getting Started

You can write a flow in a few lines of code:
``` python
from xyzflow import Parameter

# Define parameters
x = Parameter(value=10, description="X")
y = Parameter(value=10, description="Y")
  
def main():
    return x + y
       
if __name__ == "__main__":   
    print(main()()) # Execute flow and print the result
```

A flow consists out of:
1) Parameter definitions in the global scope
2) A `main()` method that returns the resulting Task
3) Optionally: A main if clause that executes your defined flow

### How does it work?

Everything is a `Task` (even Parameters). Inside of the `main()` you define a flow. 
A flow is a sequence of tasks that shall be executed. You can give the results of a task as input parameter to another task.
That way, we create an execution graph.
Any task can be evaluted at any time with the `()` operator.
The result can be used to continue with a flow or just to get the final result of a flow.
