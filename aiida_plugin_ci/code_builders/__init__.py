"""
Module to manage code builders

In particular, contains a CODE_BUILDERS dictionary that maps to the 
respective classes
"""
from .singularityhub import SingularityHub

CODE_BUILDERS = {
    'singularityhub': SingularityHub,
}
