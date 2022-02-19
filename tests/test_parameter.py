from xyzflow import Parameter
import pytest

def test_add():
    a = Parameter(value=1)
    b = Parameter(value=2)
    c = a+b
    assert c().result == 3
    