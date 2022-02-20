from typing import Union
from unittest import TextTestRunner
import networkx as nx
import matplotlib.pyplot as plt
import threading
from diskcache import Cache
import pickle
import inspect
import time
import os
import argparse
import importlib.util
from pprint import pprint
from colorama import Back, Style, Fore
from tabulate import tabulate
import pandas as pd
import sys

from .Flow import get_flow_parameter
from .Task import Task

    
    
      
def inspect_parameters(args):
    
    spec = importlib.util.spec_from_file_location("flow", args.py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parameters = get_flow_parameter(module)
    pprint(parameters)
    return parameters
    
    
def main(): 
    parser = argparse.ArgumentParser(description='XYZflow cli tool')
    
    subparsers = parser.add_subparsers(help='commands')
    parser_parameters = subparsers.add_parser('parameters', help='Inspect a flow and print out all input parameters')
    parser_parameters.add_argument('py', help='Python file containing the flow (must have a main())')
    parser_parameters.set_defaults(func=inspect_parameters)
    
    args = parser.parse_args(sys.argv[1:])
    args.func(args)