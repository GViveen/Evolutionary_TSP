# Overview

This repository contains a Python implementation of a simple evolutionary algorithm to solve the Travelling Salesman Problem (TSP). Inputs are either from a predefined file (file-tsp.txt) or from any of the benchmark files available at the [TSPLib](http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsplib.html).

# Requirements

You'll need Python 3.x to be able to run this project. Additionally, the project relies on a number of additional packages:
* numpy
* tqdm
* tsplib95
* matplotlib

All of the above packages are available via the pip installer. Apart from tsplib95, they are also available via the conda package manager. 
To easily set up your own environment with these packages installes you can either use pip to run `pip install -r requirements.txt` or to use conda with `conda install -r requirements.txt`. Note that if you use the conda installation you will still need to use pip to install tsplib95 if you want to use this project along with any input files from TSPLib.

# Instructions

If all packages are installed and the repo is cloned, navigate to the folder containing `main.py`. To do a short test run, enter something similar to:
```python
python main.py --file "file-tsp.txt" --pop_size 25 --generations 100
```

To do a test run with a memetic algorithm, run something similar to:
```python
python main.py --file "file-tsp.txt" --pop_size 25 --generations 100 --memetic
```

The full set of command line arguments is:
* `--file` controls the input file. This file must be located in the tsp folder. Default: `"file-tsp.txt"`
* `--pop_size` controls how many individuals are present in each generation. Default: `100`
* `--generations` controls for how many generations the algorithm should run. Default: `10000`
* `--mutation_rate` controls the mutation rate for each child. Default: `0.005`
* `--memetic` controls whether the algorithm runs a 2-opt local search to improve convergence. Default: `False`
