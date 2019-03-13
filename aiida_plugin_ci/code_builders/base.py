"""
Module containing the base class for builders
"""
import abc

class CodeBuilder(object):
    """
    Base class for a builder
    """
    @abc.abstractmethod
    def build(self):
        """
        Build or fetch the code and drop it in a given location that AiiDA
        will be able to find later
        """

    @abc.abstractmethod
    def get_full_exec_command(self):
        """
        Get the full execution command (as a string) 
        that can be used by AiiDA to execute the code

        In the future, extend it to a list of string? Requires adaptation in AiiDA
        """

    def setup_aiida_code(self, input_plugin_name, code_name):
        """
        Setup the code in AiiDA.

        It expects to find already an AiiDA computer, named 'localhost', 
        and setup with a local transport.

        It returns the configured AiiDA code.
        """
        from aiida.orm import Computer, Code

        computer = Computer.objects.get(name='localhost')
        code = Code(
            remote_computer_exec=(computer, self.get_full_exec_command()), 
            input_plugin_name=input_plugin_name, label=code_name)
        code.store()
        return code

    @classmethod
    @abc.abstractmethod
    def print_status(self):
        """
        Print information on the status of required dependencies
        """
