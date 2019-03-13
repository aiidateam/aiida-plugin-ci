"""
Module that contains utility functions to autodiscover tests and to run them
"""
from __future__ import print_function, absolute_import

import pkgutil
import inspect
import json

from . import TestProcessPlugin

def get_test_classes(test_dir):
    """
    Find all tests in the test_dir directory, defined as:

    - valid python modules
    - filename starting with ``test_``
    """
    ret_dict = {}
    for importer, package_name, _ in pkgutil.iter_modules([test_dir]):
        if not package_name.startswith('test_'):
            continue
        loader = importer.find_module(package_name)
        module = loader.load_module(package_name)
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                    issubclass(obj, TestProcessPlugin) and
                    obj != TestProcessPlugin):
                ret_dict["{}.{}".format(package_name, name)] = obj
    return ret_dict

def describe(test_dir):
    """
    Autodiscover all tests and print their description
    """
    for test_name, test_class in get_test_classes(test_dir).items():
        print("**** {} ****".format(test_name))
        test_class.print_description()

def autorun(test_dir, verbose):
    """
    Autodiscover all tests and run them
    """
    full_status = {}

    for test_name, test_class in get_test_classes(test_dir).items():
        print("**** {} ****".format(test_name))
        # instantiate and run
        status = test_class().run(verbose=verbose)
        full_status[test_name] = status
    
    print(json.dumps(full_status, sort_keys=True, indent=2))

def print_aiida_version():
    """
    Print the AiiDA version in the current virtual env.
    """
    try:
        import aiida
        version = aiida.__version__
    except ImportError:
        print("- AiiDA: missing, unable to import")
    else:
        print("- AiiDA: version {}".format(version))

def status():
    """
    Print status information
    """
    import sys
    from .code_builders import CODE_BUILDERS

    print("*** Python version")
    print(sys.version)
    
    print("*** AiiDA version")
    print_aiida_version()

    for code_builder_name in sorted(CODE_BUILDERS):
        code_builder_class = CODE_BUILDERS[code_builder_name]
        print("*** CODE BUILDER '{}'".format(code_builder_name))
        code_builder_class.print_status()
    