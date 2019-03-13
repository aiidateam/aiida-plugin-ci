#!/usr/bin/env runaiida
from __future__ import print_function

import sys

from aiida_plugin_ci.utils import autorun, describe, status

TEST_FOLDER = 'test_examples'

if __name__ == "__main__":
    if sys.argv[1:2] == ['-v']:
        describe(TEST_FOLDER)
    elif sys.argv[1:2] == ['-s']:
        status()
    elif sys.argv[1:2] == []:
        autorun(TEST_FOLDER, verbose=True)
    else:
        print("Pass either -v or no cmdline parameter", file=sys.stderr)
        sys.exit(1)
