import os
import io

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

modulename = 'aiida_plugin_ci'
the_license = "The MIT license"

# Get the version number in a dirty way
folder = os.path.split(os.path.abspath(__file__))[0]
fname = os.path.join(folder, modulename, '__init__.py')
with open(fname) as init:
    ns = {}
    # Get lines that match, remove comment part
    # (assuming it's not in the string...)
    versionlines = [
        l.partition('#')[0]
        for l in init.readlines()
        if l.startswith('__version__')
    ]
if len(versionlines) != 1:
    raise ValueError("Unable to detect the version lines")
versionline = versionlines[0]
version = versionline.partition('=')[2].replace('"', '').strip()

setup(
    name=modulename,
    description=
    "A module to perform continuous integration AiiDA plugins",
    url='http://github.com/aiidateam/aiida-plugin-ci',
    license=the_license,
    author='Giovanni Pizzi',
    version=version,
    install_requires=[],
    extras_require={
    },
    packages=find_packages(),
    # Needed to include some static files declared in MANIFEST.in
    include_package_data=True,
    download_url='https://github.com/aiidateam/aiida-plugin-ci/archive/v{}.tar.gz'.
    format(version),
    keywords=[
        'AiiDA', 'plugin', 'test', 'singularity', 'continuous integration'
    ],
    #long_description=io.open(
    #    os.path.join(folder, 'README.rst'), encoding="utf-8").read(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
