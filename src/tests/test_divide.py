import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import dummy

def test_divide():
    assert 0 == dummy.divide(0, 0)
    assert 2 == dummy.divide(4, 2)
