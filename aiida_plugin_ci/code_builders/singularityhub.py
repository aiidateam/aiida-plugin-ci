"""
Builder for singularity files using Singularity hub
"""
import contextlib
import os
import subprocess

from .base import CodeBuilder

# Images could go to SINGULARITY_CACHEDIR if we use 'singularity run' for instance
# instead of 'singularity pull'. To check, this would avoid the need of a caching dir
SINGULARITY_IMAGES_DIR = '/tmp/singularity-images'

@contextlib.contextmanager
def cd(path, create=False):
    current_dir = os.getcwd()
    
    if create and not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    try:
        yield
    #except:
    #    print 'Exception caught: ',sys.exc_info()[0]
    finally:
        os.chdir(current_dir)

class SingularityHub(CodeBuilder):
    """
    Builder fetching an image from a Singularity Hub
    (by default singularity-hub.org)
    """
    def __init__( # pylint: disable=too-many-arguments
        self, username, reponame, registry=None, tag=None, 
        commit=None, exec_command=None):  
        """
        Setup a builder. 

        Only username and reponame are required.
        The syntax and the meaning of parameters can be found here:
        https://github.com/singularityhub/singularityhub.github.io/wiki/Build-A-Container#referencing-containers
        If you specify a commit, you should also specify a tag
        """
        self._username = username
        self._reponame = reponame
        self._registry = registry
        self._tag = tag
        self._commit = commit
        self._exec_command = exec_command

        if self._exec_command is not None:
            raise NotImplementedError('Not yet implemented, might require changes in AiiDA')
    
    def get_image_filename(self):
        """Return a valid filename for the image"""
        registry = getattr(self, '_registry', None)
        return "{}{}{}-{}-{}{}{}.simg".format(
            registry or "",
            "-" if registry else "",
            self._username,
            self._reponame,
            getattr(self, '_tag', 'latest'),
            "-" if self._commit else "",
            self._commit or ""
        )

    def get_image_full_path(self):
        """
        Return full absolute path to the where the image will be
        (once built/fetched)
        """
        return os.path.abspath(os.path.join(SINGULARITY_IMAGES_DIR, self.get_image_filename()))

    def get_pull_string(self):
        """
        Return a string that can be used to reference the container in a 
        ``singularity pull`` command
        """
        return "shub://{}{}{}/{}{}{}{}{}".format(
            self._registry or "",
            "/" if self._registry else "",
            self._username,
            self._reponame,
            ":" if self._tag else "",
            self._tag or "",
            "@" if self._commit else "",
            self._commit or ""
        )

    def build(self):
        """
        Build or fetch the code
        """
        from subprocess import CalledProcessError

        with cd(SINGULARITY_IMAGES_DIR, create=True):
            out = subprocess.check_output(                
                ['singularity', 'pull', '--name', self.get_image_filename(), 
                self.get_pull_string()])
                

        # Note that if the file was there and the previous command failed
        # This will not raise.
        # However, it should be ok as singularity in that case would return
        # a non-zero error code and therefore there would be an exception
        assert os.path.isfile(self.get_image_full_path()), "No image file was built"

    def get_full_exec_command(self):
        """
        Get the full execution command (as a string)

        In the future, extend it to a list of string? Requires adaptation in AiiDA
        """
        full_exec_command = self.get_image_full_path()
        if self._exec_command:
            full_exec_command.append(self._exec_command)
            raise NotImplementedError('Not yet implemented, might require changes in AiiDA')
        return full_exec_command
        
    @classmethod
    def print_status(self):
        """
        Print information on the status of required dependencies
        """
        from subprocess import CalledProcessError

        full_exec_command = ['singularity', '--version']
        try:
            output = subprocess.check_output(full_exec_command)
        except CalledProcessError:
            print("- SINGULARITY: 'singularity --version' returned an error")
        except OSError:
            print("- SINGULARITY: 'singularity' binary not found")
        else:
            print("- SINGULARITY: version {}".format(output.strip()))
