### Model Validation Overview

In §4 of our paper, we run some experiments to evaluate our modeling tools and Shadow improvements. In this page, we provide some details about the config files and data that can be used to reproduce our results.

### Tor Model Configs

Our analysis included some results from simulations using Shadow. We generated ten 31% and three 100% Tor model configuration bundles using the process described on [the process page](/process), and provide the configs in the [the configs directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/model_validation/configs). The CCS 2018 model was taken from [previous work](https://tmodel-ccs2018.github.io/data/shadow/hosts/shadowtor-2000r-129419c-privcount-config.tar.xz).

The experiments with the 31% networks were run on `CentOS Linux release 7.6.1810 (Core)` using Kernel `4.4.178-1.el7.elrepo.x86_64 #1 SMP Wed Apr 3 05:46:30 EDT 2019 x86_64`.

The experiments with the 100% networks were run on `Ubuntu 18.04.4 LTS` using Kernel `4.15.0-109-generic #110-Ubuntu SMP Tue Jun 23 02:39:32 UTC 2020 x86_64`.

The extracted results from the simulations are provided in [the data directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/model_validation/data).

### Reproducing the graphs

To reproduce the graphs in §4 of our paper, run the following from [the model_validation directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/model_validation):

```
# create the python virtual environment
python3 -m venv ~/venvs/nevenufenv
source ~/venvs/nevenufenv/bin/activate
pip3 install numpy scipy matplotlib

# plot the figures from the paper
PYTHONPATH=../process python3 plot_figure1.py
PYTHONPATH=../process python3 plot_figure2.py -i data
PYTHONPATH=../process python3 plot_figure3.py -i data

# write some stats
python3 print_resource_usage.py > resource_usage.txt
```

### Results

- [Figure 1](figure1.pdf)
- Figures [2a](figure2a.pdf), [2b](figure2b.pdf), [2c](figure2c.pdf), [2d](figure2d.pdf), [2e](figure2e.pdf), [2f](figure2f.pdf), [2g](figure2g.pdf), [2h](figure2h.pdf), related [statistics](figure2_stats.txt), [y label](figure2_ylabel.pdf), and [legend](figure2_legend.pdf)
- Figures [3a](figure3a.pdf), [3b](figure3b.pdf), [3c](figure3c.pdf), [3d](figure3d.pdf), [3e](figure3e.pdf), [3f](figure3f.pdf), [3g](figure3g.pdf), [3h](figure3h.pdf), related [statistics](figure3_stats.txt), [y label](figure3_ylabel.pdf), and [legend](figure3_legend.pdf)
- [Resource usage statistics](resource_usage.txt)

### Reproducing the Tor Metrics Analysis

Our analysis compares results from Shadow to results from Tor metrics. We wrote some scripts to assist in processing Tor metrics data and prepare it for comparing to Shadow results. The result of the Tor metrics analysis have been cached in [the model_validation/data/tor directory](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/model_validation/data/tor), but we provide the steps we followed in our analysis for posterity.

```
# update the python virtual environment
source ~/venvs/nevenufenv/bin/activate
pip3 install stem

# create the directory to store the output
mkdir -p data/tor
```

#### Tor Relay Churn

We process the consensus files in our analysis of relay churn.

```
# Download the data from Tor
wget https://collector.torproject.org/archive/relay-descriptors/consensuses/consensuses-2019-01.tar.xz
tar xJf consensuses-2019-01.tar.xz

# Run the analysis
python3 parse_tor_churn.py consensuses-2019-01
```

#### Tor Relay Goodput

We use data about Tor relay goodput over time.

```
# Download the data from Tor
for y in 2018 2019
do
  wget -O data/tor/bandwidth-${y}-01-01-${y}-12-31.csv "https://metrics.torproject.org/bandwidth.csv?start=${y}-01-01&end=${y}-12-31"
done
```

#### Tor Client Performance

We also use some of the performance data visualized on the [Tor metrics torperf page](https://metrics.torproject.org/torperf.html). The process for computing the metrics is documented by the Tor Project on [the reproducible metrics page](https://metrics.torproject.org/reproducible-metrics.html#performance).

```
# Download the data from Tor
for y in 2018 2019
do
  mkdir torperf-${y}
  cd torperf-${y}
  for m in 01 02 03 04 05 06 07 08 09 10 11 12
  do
    wget https://collector.torproject.org/archive/torperf/torperf-${y}-${m}.tar.xz
    tar xJf torperf-${y}-${m}.tar.xz
    rm torperf-${y}-${m}.tar.xz
  done
  cd ..
done

# Run the analysis
python3 parse_tor_perf.py
```
