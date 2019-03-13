"""
Functionality to run tests for the plugins
"""
from __future__ import print_function, absolute_import

import functools
import inspect
import traceback

from collections import namedtuple

from aiida.plugins.entry_point import load_entry_point_from_string
from aiida.engine import run_get_node

from .code_builders import CODE_BUILDERS

SingleTest = namedtuple(
    'SingleTest', 
    ['priority', 'test_function_name', 'entrypoint_name', 'generate_function', 'test_function'])

def process_test(priority, entrypoint_name, generate_function):
    """A decorator to mark test for a given Process class defined in a plugin"""
    def decorator_function(func):
        func._test_method_data = {  # pylint: disable=protected-access
            'priority': priority,
            'entrypoint_name': entrypoint_name,
            'generate_function': generate_function
        }

        @functools.wraps(func)
        def wrapper_function(*args, **kwargs):
            # Do stuff
            return func(*args, **kwargs)
        return wrapper_function
    return decorator_function


class TestProcessPlugin(object):
    """
    Base implementation 
    """
    code_resources = None # Should be a dict
    
    def setup_codes(self):
        """Implemented in the base class.

        Reads the ``self.code_resources`` specification, installs the codes and creates AiiDA ``Code`` instances that can be
        retrieved from the test class through the ``codes`` property that returns a dictionary of ``Code`` instances.

        After being called, self.codes will be a dictionary with the same keys as ``self.code_resources``, the value
        being a stored AiiDA Code configured for the code as declared in ``self.code_resources``.

        .. note:: If you want to add more things and you subclass this, do not forget to call the super().
        """
        success = True
        info = {}

        code_resources = self.code_resources
        if code_resources is None:
            code_resources = {}
        
        self.codes = {}
        for code_name, code_declaration in code_resources.items():
            try:
                code_builder = CODE_BUILDERS[code_declaration['type']](
                    **code_declaration['parameters']
                )
            except Exception as exception:
                status = {}
                self._set_exception_to_status(status, 'FETCHING_BUILDER_FAILED', exception)
                info[code_name] = status
                success = False
                continue

            try:
                code_builder.build()
            except Exception as exception:
                status = {}
                self._set_exception_to_status(status, 'BUILDING_CODE_FAILED', exception)
                info[code_name] = status
                success = False
                continue

            try:
                aiida_code = code_builder.setup_aiida_code(
                    input_plugin_name=code_declaration.get('input_plugin_name', None), 
                    code_name=code_name)
            except Exception as exception:
                status = {}
                self._set_exception_to_status(status, 'SETUP_AIIDA_CODE_FAILED', exception)
                info[code_name] = status
                success = False
                continue
            
            self.codes[code_name] = aiida_code
    
        return success, info

    def setup_resources(self):
        """
        Setup some resources (i.e., load some data in the database). 
        
        By default, no resources are setup, you can extend this in a plugin.
        If you create data and you want to reference it, you can set it into
        ``self`` to be reused in later methods.
        """
            
    @classmethod
    def defines_custom_resources(cls):
        return cls.setup_resources != TestProcessPlugin.setup_resources

    @classmethod
    def print_description(cls):
        if cls.defines_custom_resources():
            print("  * Test will setup custom resources")

        if cls.code_resources:
            print("  * Codes to setup:")
            for code_name in cls.code_resources.keys(): 
                print("    - {}".format(code_name))
    
        test_methods = cls.get_tests()
        if test_methods:
            print("  * Test methods:")
            for test in test_methods:
                print("    - {} (priority {})".format(test.test_function_name, test.priority))
                print("      Generating inputs for entrypoint '{}' via function '{}'".format(
                    test.entrypoint_name, test.generate_function.__name__
                    ))

    @classmethod
    def get_tests(cls): 
        """Get all tests in a sorted list"""

        test_methods = {}

        for name, test_function in inspect.getmembers(cls):
            # both so that it works both as a classmethod and as a normal method
            if (inspect.isfunction(test_function) or inspect.ismethod(test_function)) and name.startswith('test_'):
                # This is set by the decorator
                test_method_data = getattr(test_function, '_test_method_data', None)
                if test_method_data is None:
                    continue
                # Sorted in this way to sort first by priority, then by name
                test_methods[(test_method_data['priority'], name)] = (
                    test_method_data['entrypoint_name'],
                    test_method_data['generate_function'],
                    test_function,
                )

        test_list = []
        for priority, name in sorted(test_methods):
            test = test_methods[(priority, name)]
            test_list.append(SingleTest(
                priority = priority, 
                test_function_name = name,
                entrypoint_name = test[0],
                generate_function = test[1],
                test_function = test[2]
            ))
        
        return test_list

    @staticmethod
    def _set_exception_to_status(status_dict, status_string, exception):
        """
        Set correct keys in the status_dict in case an exception is raised
        """
        status_dict['status'] = status_string
        status_dict['exception_traceback'] = traceback.format_exc()
        status_dict['exception_message'] = str(exception)
        status_dict['exception_class'] = exception.__class__.__name__

    def _run_get_status(self, ProcessClass, inputs, test_function):
        status = {}

        try:
            _, process_node = run_get_node(ProcessClass, **inputs)
        except Exception as exc:
            self._set_exception_to_status(status, 'ENGINE_RUN_EXCEPTED', exc)
            return status

        # aiida.engine.run() didn't crash
        try:
            status['ret_code'] = test_function(self, process_node)
        except Exception as exc:
            self._set_exception_to_status(status, 'TEST_FUNCTION_EXCEPTED', exc)
            return status

        # test_function() didn't crash
        if 'ret_code' in status and (status['ret_code'] == 0 or status['ret_code'] is None):
            status['status'] = 'SUCCESS'
        else:
            status['status'] = 'TEST_FAILED'

        return status


    def run(self, verbose=False):
        """
        Run all tests in the class in the order specified by the priorities
        """
        run_status = {}
        success, info = self.setup_codes()
        if verbose:
            print("  -> Codes setup: {}".format("SUCCESS" if success else "FAILED"))
        if not success:
            print("     FAILED WHILE SETTING UP THE FOLLOWING CODES:")
            for key in info:
                print("       * {}".format(key))
                print("         {}".format(info[key]))
            return run_status

        self.setup_resources()
        if verbose:
            print("  -> Resources setup")

        for test in self.get_tests():
            test_status = {}

            try:
                ProcessClass = load_entry_point_from_string(test.entrypoint_name)
            except Exception as exc:
                self._set_exception_to_status(
                    test_status, 'CALCULATION_ENTRYPOINT_LOADING_FAILED', exc)
                run_status[test.test_function_name] = test_status
                continue

            try:
                inputs = test.generate_function(self)
            except Exception as exc:
                self._set_exception_to_status(
                    test_status, 'GENERATE_INPUTS_FAILED', exc)
                run_status[test.test_function_name] = test_status
                continue

            test_status = self._run_get_status(ProcessClass, inputs, test.test_function)
            run_status[test.test_function_name] = test_status

            if verbose:
                print("  -> test '{}' run, status: {}".format(
                    test.test_function_name, test_status.get('status', "UNKNOWN")
                ))
        return run_status
