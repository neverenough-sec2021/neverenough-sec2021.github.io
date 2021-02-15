#!/usr/bin/python

import sys
import logging

import matplotlib
matplotlib.use('Agg') # for systems without X11
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_pdf import PdfPages

from plot_common import *

def main():
    args = get_args()
    setup_logging(args.logfile)
    run(args)
    logging.info("All done!")

def load_data(args, ttb_key):
    logging.info("Searching for tgen stats files in {}".format(args.inpath))
    tgen_stats_paths = get_filepaths(args.inpath, ttb_key)
    logging.info("Found {} total tgen stats files".format(len(tgen_stats_paths)))

    db = {}

    for path in tgen_stats_paths:
        logging.info("Loading data from {}".format(path))

        load = get_load_percentage(path)
        if load != "1.0":
            continue

        net = get_net(path)
        seed = get_seed(path)

        db.setdefault(net, {})
        db[net].setdefault(seed, {'all': [], '51200': [], '1048576': [], '5242880': []})

        data = load_json(path)

        for key in db[net][seed].keys():
            if key in data:
                db[net][seed][key].extend(data[key])

    return db

def run(args):
    logging.info("Loading data")
    ttfb_db = load_data(args, "time_to_first_byte_recv")
    ttlb_db = load_data(args, "time_to_last_byte_recv")

    logging.info("Starting to plot")
    set_plot_options()

    fig = pyplot.figure()

    net_colors = {'a':'C0', 'b':'C1', 'c':'C2'}
    net_names = {'a':'1', 'b':'2', 'c':'3'}
    seed_lines = {'1':'-', '2':'--', '3':':'}

    lines = []
    labels = []

    for net in sorted(ttlb_db.keys()):
        for seed in sorted(ttlb_db[net].keys()):
            i = net_names[net]
            j = seed
            label = "$\widetilde{{F}}_{{X{i}{j}}}$".format(i=i, j=j)
            labels.append(label)

            x, y = getcdf(ttlb_db[net][seed]['51200'])
            l = pyplot.plot(x, y, label=label, color=net_colors[net], linestyle=seed_lines[seed])
            lines.append(l[0])

    pyplot.xlabel("Download Time (s)")
    pyplot.ylabel("Empirical CDF")
    pyplot.xlim(xmin=-.25, xmax=7.25)
    #pyplot.yscale("taillog")

    pyplot.legend(ncol=3)
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("figure6.pdf")

    # dump the legend
    #f = pyplot.figure(figsize=(4,.85))
    #f.legend(lines, labels, ncol=3, loc='center')
    #f.tight_layout(pad=0.3)
    #f.savefig("figure6_legend.pdf")

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
