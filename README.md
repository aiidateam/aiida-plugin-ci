# aiida-plugin-ci

A suite to perform Continuous Integration of AiiDA plugins

## NOTES
- for Singularity, if your AiiDA run directory is not in a standard partition
  (e.g. it's in a filesystem mounted on `/scratch`) you have to tell 
  Singularity to also mount that volume.
  To do this, add the following to your `~/.bashrc`:
  ```
  export SINGULARITY_BINDPATH="/scratch" 
  ```
  (see e.g. https://singularity.lbl.gov/docs-mount#specifying-bind-paths)

- at the moment, to run, use:

  - `./run_tests.py` to run the tests and get a report
  - `./run_tests.py -v` to run a dry-run inspecting the tests
  - `./run_tests.py -s` to check the status of the dependencies (singularity, aiida)

