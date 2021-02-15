### Significance Analysis Overview

In §5 of our paper, we describe an analysis methodology that allows us to compute confidence intervals over a set of simulations results, in order to make more informed inferences about Tor network performance. In this page, we provide some details about the config files and data that can be used to reproduce our results.

### Tor Model Configs

Our significance analysis included some results from simulations using Shadow. We generated 3 Tor model configuration bundles using the process described on [the process page](/process).

The above produces 3 Tor models for Shadow, which we provide in the [the configs directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/significance_analysis/configs). We ran each of them 3 times using unique seeds (using Shadow's `--seed` command line option).

The experiments were run on `CentOS Linux release 7.6.1810 (Core)` using Kernel `4.4.178-1.el7.elrepo.x86_64 #1 SMP Wed Apr 3 05:46:30 EDT 2019 x86_64`.

The extracted results are provided in [the data directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/significance_analysis/data).

### Reproducing the graphs

To reproduce the graphs in §5 of our paper, run the following from [the significance_analysis directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/significance_analysis):

```
# create the python virtual environment
python3 -m venv ~/venvs/nevenufenv
source ~/venvs/nevenufenv/bin/activate
pip3 install numpy scipy matplotlib

# plot the figures from the paper
python3 plot_figure4.py
python3 plot_figure5.py
PYTHONPATH=../process python3 plot_figure6.py -i data

# write some stats
PYTHONPATH=../process python3 print_resource_usage.py -i data
```

### Results

- Figures [4a](figure4a.pdf), [4b](figure4b.pdf), and [5](figure5.pdf)
- Figure [6](figure6.pdf) and related [statistics](resource_usage.txt)
