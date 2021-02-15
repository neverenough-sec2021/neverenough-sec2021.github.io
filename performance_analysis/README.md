### Performance Analysis Case Study Overview

In §6 of our paper, we present the results of a case study of the effects of an increase in Tor usage on Tor client performance. In this page, we provide some details about the config files and data that can be used to reproduce our results.

### Tor Model Configs

Our performance analysis included some results from simulations using Shadow. We generated 420 Tor model configuration bundles using the process described on [the process page](/process) using the parameters shown in Table 4 in the paper, and provide the configs in the [the configs directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/performance_analysis/configs).

The experiments were run on `CentOS Linux release 7.6.1810 (Core)` using Kernel `4.4.178-1.el7.elrepo.x86_64 #1 SMP Wed Apr 3 05:46:30 EDT 2019 x86_64`.

The extracted results from the simulations are provided in the data directories for [the 1 percent](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/performance_analysis/data_1percent), [the 10 percent](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/performance_analysis/data_10percent), and [the 30 percent](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/performance_analysis/data_30percent) networks.

### Reproducing the graphs

To reproduce the graphs in §6 of our paper (and Appendix D in the full version), run the following from [the performance_analysis directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/performance_analysis):

```
# create the python virtual environment
python3 -m venv ~/venvs/nevenufenv
source ~/venvs/nevenufenv/bin/activate
pip3 install numpy scipy matplotlib

# plot the figures from the paper
PYTHONPATH=../process python3 plot_figures_7_9_10_11.py
PYTHONPATH=../process python3 plot_figure8.py
PYTHONPATH=../process python3 plot_figure12.py

# write some stats
PYTHONPATH=../process python3 print_resource_usage.py -i .
```

### Results

Figures [7a](figure7a.pdf), [7b](figure7b.pdf), [7c](figure7c.pdf), [8a](figure8a.pdf), [8b](figure8b.pdf), [8c](figure8c.pdf), [9a](figure9a.pdf), [9b](figure9b.pdf), [9c](figure9c.pdf), [10a](figure10a.pdf), [10b](figure10b.pdf), [10c](figure10c.pdf), [11a](figure11a.pdf), [11b](figure11b.pdf), [11c](figure11c.pdf), [12a](figure12a.pdf), [12b](figure12b.pdf), [12c](figure12c.pdf), and related [statistics](resource_usage.txt)