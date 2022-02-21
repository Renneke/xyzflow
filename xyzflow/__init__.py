#
# XYZFlow - Simple Orchestration Framework
#

from .Task import Task, task
from .Flow import get_flow_parameter, flow
from .HelperTasks import Add, Sub, Multiplication
from .Parameter import Parameter
from .xyzflow import inspect_parameters, main