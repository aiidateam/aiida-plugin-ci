"""
Some example plugin tests as a demonstrator
"""
from __future__ import print_function, absolute_import

from aiida_plugin_ci import TestProcessPlugin, process_test

class CustomTest(TestProcessPlugin):
    """A simple test"""
    
    code_resources = {
        'doubler': {
            'type': 'singularityhub',
            'parameters': {
                #'registry': 'singularity-hub.org', # Optional
                'username': 'giovannipizzi',
                'reponame': 'singularity-doubler',
                # 'tag': 'latest', # optional
                # 'commit': None # optional
                # 'exec_command': None # Not implemented yet!
            },
            'input_plugin_name': 'templatereplacer'
        },
    }

    def setup_resources(self):
        """
        Setup some resources into the DB only once for all tests
        """
        from aiida.orm import Dict

        self.template = Dict(dict={
            'cmdline_params': ["1"],
            'input_file_template': "{value}",  # File just contains the value to double
            'input_file_name': 'value_to_double.txt',
            'output_file_name': 'output.txt',
            'retrieve_temporary_files': ['triple_value.tmp']
        }).store()

        self.options_dict = {
            'resources': {
                'num_machines': 1
            },
            'max_wallclock_seconds': 5 * 60,
            'withmpi': False,
            'parser_name': 'templatereplacer.doubler',
        }
    
    def generate_inputs_1(self):
        """Generate a basic input"""
        from aiida.orm import Dict

        inputs = {
            'code': self.codes['doubler'],
            'parameters': Dict(dict={'value': 3}),
            'template': self.template,
            'metadata': {
                'options': self.options_dict,
            }
        }
        return inputs

    @process_test(400, 'aiida.calculations:templatereplacer', generate_inputs_1)
    def test_1(self, node):
        """Perform some tests"""
        assert node.outputs.output_parameters.dict.value == 2 * 3, "Wrong value for 'outputs_parameters.value'"
        # 'retrieved_temporary_files': {'triple_value.tmp': str(inputval * 3)}

# class PwTest(TestProcessPlugin):
#     """A simple test for Quantum ESPRESSO pw.x"""
    
#     code_resources = {
#         'pw': {
#             'type': 'singularityhub',
#             'parameters': {
#                 'username': 'giovannipizzi',
#                 'reponame': 'singularity-quantum-espresso',
#                 'tag': 'apt-5.1-pw.x',
#                 # 'exec_command': 'pw.x' # Not implemented yet!
#             },
#             'input_plugin_name': 'quantumespresso.pw'
#         },     
#     }

#     def setup_resources(self):
#         """
#         Setup some resources into the DB only once for all tests
#         """
#         from aiida.orm import Dict

#         self.template = Dict(dict={
#             'cmdline_params': ["1"],
#             'input_file_template': "{value}",  # File just contains the value to double
#             'input_file_name': 'value_to_double.txt',
#             'output_file_name': 'output.txt',
#             'retrieve_temporary_files': ['triple_value.tmp']
#         }).store()

#         self.options_dict = {
#             'resources': {
#                 'num_machines': 1
#             },
#             'max_wallclock_seconds': 5 * 60,
#             'withmpi': False,
#             'parser_name': 'templatereplacer.doubler',
#         }
    
#     def generate_inputs_1(self):
#         """Generate a basic input"""
#         from aiida.orm import Dict

#         inputs = {
#             'code': self.codes['pw'],
#             'parameters': Dict(dict={'value': 3}),
#             'template': self.template,
#             'metadata': {
#                 'options': self.options_dict,
#             }
#         }
#         return inputs

#     @process_test(400, 'aiida.calculations:quantumespresso.pw', generate_inputs_1)
#     def test_pw(self, node):
#         """Perform some tests"""
#         assert node.outputs.output_parameters.dict.value == 2 * 3, "Wrong value for 'outputs_parameters.value"
#         # 'retrieved_temporary_files': {'triple_value.tmp': str(inputval * 3)}


#     #@process_test(200, 'aiida.calculations:templatereplacer', generate_inputs_2)
#     #def test_3(self, node):
#     #    """Perform some tests"""
#     #    pass


class FailingTest(TestProcessPlugin):
    """A simple test that fails early"""
    
    def generate_inputs(self):  # pylint: disable=no-self-use
        """Generate a basic input"""
        raise ValueError("Check that raising works correctly")

    @process_test(400, 'aiida.calculations:templatereplacer', generate_inputs)
    def test_example(self, node): 
        """Perform some tests"""
