## About
This script reproduces the results from the evaluation section in [1].

## Prerequisites
The scripts given here use [apssh](https://github.com/parmentelat/apssh) and [asynciojobs](https://github.com/parmentelat/asynciojobs) to remotely run parallel commands on a number of nodes. First make sure you have a recent version of Python (>= 3.6), then install those on your computer:
```
pip3 install apssh asynciojobs
```
You also need to have a slice in R2Lab and your computer must be able to log onto the gatewy node. If this is not the case already, you can ask to [register](https://r2lab.inria.fr/tuto-010-registration.md) for an account.

The data analysis and plotting script is provided as a Jupyter notebook. You can either install `jupyter-lab` and run it locally, or use a cloud server, e.g. Google Colab.

## Usage
First create a directory where the experiment data will be downloaded, then save its path in the `PATH` variable of the scripts. You can then run the experiment on R2Lab:
```
python3 agent.py
```

Once the experiment is finished (around 10 minutes), you can start analysing the data and reproducing the figures in the paper. The code to do so is available in the notebook.
