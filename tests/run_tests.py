# python libraries
# NOTE: switch python PATH to look at parent_directory
import os, sys, inspect
parent_directory = os.path.dirname(\
                    os.path.dirname(\
                    os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0,parent_directory)
import unittest

from tests.test_intersect import TestIntersect

if __name__ == '__main__':
    unittest.main()