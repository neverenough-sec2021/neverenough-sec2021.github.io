#!/usr/bin/env python

import sys

import matplotlib
import matplotlib.pyplot as pyplot

from random import sample
from numpy import isnan, arange, std, mean, sqrt, quantile
from numpy.random import normal
from scipy.stats import t, norm

def generate_result_list(sample_size):
    sample_loc = normal(loc=0.0, scale=1.0)
    sample_scale = normal(loc=1.0, scale=1.0)**2
    results = list(normal(loc=sample_loc, scale=sample_scale, size=sample_size))
    return results

def get_err_factor(k, ci_level=0.95):
    return t.ppf(ci_level/2 + 0.5, k-1)/sqrt(k-1)

def get_stdev_factor(q, loc=1):
    return abs(norm.ppf(q, loc=loc))

def main():
    set_plot_options()
    run_analytical()
    #run_experimental()

def run_analytical():
    quantiles_to_plot = [.5, .9, .99]
    num_networks = 100
    confidence = 0.95

    fig = pyplot.figure()

    x = list(range(2, num_networks+1))

    y = {q:[] for q in quantiles_to_plot}
    for num_nets in x:
        e = get_err_factor(num_nets, confidence)
        for q in y:
            s = get_stdev_factor(q)
            y[q].append(2*e*s)

    pyplot.plot(x, y[.5], ls='-', label="$\sigma$ $\sim$ $\mathcal{N}$(1,1) at P50")
    pyplot.plot(x, y[.9], ls='--', label="$\sigma$ $\sim$ $\mathcal{N}$(1,1) at P90")
    pyplot.plot(x, y[.99], ls=':', label="$\sigma$ $\sim$ $\mathcal{N}$(1,1) at P99")

    pyplot.yscale("log")

    pyplot.xlabel("Number of Sampled Networks")
    pyplot.ylabel(f"Width of {int(confidence*100)}\% CI")

    pyplot.legend()
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("figure5.pdf")

def run_experimental():
    quantiles_to_plot = [.01, .1, .5, .9, .99]
    num_networks = 100
    samples_per_network = 100
    confidence = 0.95

    db = {i: generate_result_list(samples_per_network) for i in range(num_networks)}

    fig = pyplot.figure()

    for q in quantiles_to_plot:
        x, y = [], []

        for level in range(2, num_networks):
            quantile_bucket = []

            for sim in sorted(db.keys())[0:level]:
                dl_times = db[sim]
                val_at_q = quantile(dl_times, q, interpolation="lower")
                quantile_bucket.append(val_at_q)

            z = get_err_factor(level, confidence)
            k, m, s = len(quantile_bucket), mean(quantile_bucket), std(quantile_bucket)
            assert k == level

            x_left_val = m-z*s
            x_right_val = m+z*s
            width = x_right_val - x_left_val

            x.append(level)
            y.append(width)

        pyplot.plot(x, y, label=f"quantile={q}")

    pyplot.yscale("log")
    #pyplot.xscale("log")
    #pyplot.xlim(xmin=0.1, xmax=200)

    pyplot.title("number of sampled measurements per network is fixed at 100")
    pyplot.xlabel("Number of Sampled Networks")
    pyplot.ylabel(f"Width of {int(confidence*100)}\% Confidence Interval")

    pyplot.legend()
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("sig_networks_empirical.pdf")

    #########

    fig = pyplot.figure()

    x = []
    y = {}
    for size in range(1, samples_per_network+1):
        x.append(size)

        for q in quantiles_to_plot:
            quantile_bucket = []

            for sim in db:
                dl_times = db[sim][0:size]
                val_at_q = quantile(dl_times, q, interpolation="lower")
                quantile_bucket.append(val_at_q)

            z = get_err_factor(num_networks, confidence)
            k, m, s = len(quantile_bucket), mean(quantile_bucket), std(quantile_bucket)
            assert k == num_networks

            x_left_val = m-z*s
            x_right_val = m+z*s
            width = x_right_val - x_left_val

            y.setdefault(q, []).append(width)

    for q in sorted(y.keys()):
        pyplot.plot(x, y[q], label=f"quantile={q}")

    #pyplot.yscale("log")
    #pyplot.xscale("log")
    #pyplot.xlim(xmin=0.1, xmax=200)

    pyplot.title("number of sampled networks is fixed at 100")
    pyplot.xlabel("Number of Sampled Measurements per Network")
    pyplot.ylabel(f"Width of {int(confidence*100)}\% Confidence Interval")

    pyplot.legend()
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("sig_measurements_empirical.pdf")

def set_plot_options():
    options = {
        #'backend': 'PDF',
        'font.size': 12,
        'figure.figsize': (4,2),
        'figure.dpi': 100.0,
        'figure.subplot.left': 0.20,
        'figure.subplot.right': 0.97,
        'figure.subplot.bottom': 0.20,
        'figure.subplot.top': 0.90,
        'grid.color': '0.1',
        'grid.linestyle': ':',
        #'grid.linewidth': 0.5,
        'axes.grid' : True,
        #'axes.grid.axis' : 'y',
        #'axes.axisbelow': True,
        'axes.titlesize' : 'x-small',
        'axes.labelsize' : 'small',
        'axes.formatter.limits': (-4,4),
        'xtick.labelsize' : 10,#get_tick_font_size_10(),
        'ytick.labelsize' : 10,#get_tick_font_size_10(),
        'lines.linewidth' : 2.0,
        'lines.markeredgewidth' : 0.5,
        'lines.markersize' : 10,
        'legend.fontsize' : 9,
        'legend.fancybox' : False,
        'legend.shadow' : False,
        'legend.borderaxespad' : 0.5,
        'legend.numpoints' : 1,
        'legend.handletextpad' : 0.5,
        'legend.handlelength' : 2.0,
        'legend.labelspacing' : .75,
        'legend.markerscale' : 1.0,
        # turn on the following to embedd fonts; requires latex
        'ps.useafm' : True,
        'pdf.use14corefonts' : True,
        'text.usetex' : True,
    }

    for option_key in options:
        matplotlib.rcParams[option_key] = options[option_key]

    if 'figure.max_num_figures' in matplotlib.rcParams:
        matplotlib.rcParams['figure.max_num_figures'] = 50
    if 'figure.max_open_warning' in matplotlib.rcParams:
        matplotlib.rcParams['figure.max_open_warning'] = 50
    if 'legend.ncol' in matplotlib.rcParams:
        matplotlib.rcParams['legend.ncol'] = 50

if __name__ == "__main__":
    sys.exit(main())
