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

        net = get_net_instance(path)
        load = get_load_percentage(path)
        db.setdefault(load, {}).setdefault(net, {'all': [], '51200': [], '1048576': [], '5242880': []})

        data = load_json(path)

        for key in db[load][net].keys():
            if key in data:
                db[load][net][key].extend(data[key])

    return db

def run(args):
    logging.info("Loading data")
    ttfb_db, ttlb_db = {}, {}
    for scale in [1,10,30]:
        args.inpath = f"data_{scale}percent"
        ttfb_db[scale] = load_data(args, "time_to_first_byte_recv")
        ttlb_db[scale] = load_data(args, "time_to_last_byte_recv")

    logging.info("Starting to plot")
    set_plot_options()
    matplotlib.rcParams['ytick.major.pad']='0.0'

    stats_filename = "tgen-ttb-stats.txt"
    if os.path.exists(stats_filename):
        os.remove(stats_filename)

    plot(ttfb_db, "all", "Time to First Byte (s)", "ttfb", 1, [10, 100], "figure9a.pdf")
    plot(ttfb_db, "all", "Time to First Byte (s)", "ttfb", 10, [5, 10, 100], "figure9b.pdf")
    plot(ttfb_db, "all", "Time to First Byte (s)", "ttfb", 30, [5, 10], "figure9c.pdf")

    plot(ttlb_db, "51200", "Time to Last Byte (s)", "ttlb", 1, [10, 100], "figure10a.pdf")
    plot(ttlb_db, "51200", "Time to Last Byte (s)", "ttlb", 10, [5, 10, 100], "figure10b.pdf")
    plot(ttlb_db, "51200", "Time to Last Byte (s)", "ttlb", 30, [5, 10], "figure10c.pdf")

    plot(ttlb_db, "1048576", "Time to Last Byte (s)", "ttlb", 1, [10, 100], "figure7a.pdf")
    plot(ttlb_db, "1048576", "Time to Last Byte (s)", "ttlb", 10, [5, 10, 100], "figure7b.pdf")
    plot(ttlb_db, "1048576", "Time to Last Byte (s)", "ttlb", 30, [5, 10], "figure7c.pdf")

    plot(ttlb_db, "5242880", "Time to Last Byte (s)", "ttlb", 1, [10, 100], "figure11a.pdf")
    plot(ttlb_db, "5242880", "Time to Last Byte (s)", "ttlb", 10, [5, 10, 100], "figure11b.pdf")
    plot(ttlb_db, "5242880", "Time to Last Byte (s)", "ttlb", 30, [5, 10], "figure11c.pdf")


def plot(db, db_key, db_label, filename_label, scale, levels, pdf_filename):
    fig = pyplot.figure()

    load = "1.0"
    colors=["C0","C0","C0"]
    label_prefix="$\ell$=1.0, "
    draw_cdf_ci(db[scale][load], db_key, pyplot, levels=levels, colors=colors, label_prefix=label_prefix)

    load = "1.2"
    colors=["C1","C1","C1"]
    label_prefix="$\ell$=1.2, "
    draw_cdf_ci(db[scale][load], db_key, pyplot, levels=levels, colors=colors, label_prefix=label_prefix)

    pyplot.ylabel("Estimated True CDF (log scale)")
    pyplot.xlabel(db_label)

    pyplot.yscale("taillog")
    pyplot.tick_params(axis='both', which='major', labelsize=10)
    pyplot.tick_params(axis='both', which='minor', labelsize=5)
    pyplot.grid(axis='both', which='major', color='0.1', linestyle=':', linewidth='1.0')
    pyplot.grid(axis='both', which='minor', color='0.1', linestyle=':', linewidth='0.5')

    pyplot.legend(loc="lower right")
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig(pdf_filename)

def set_plot_options():
    options = {
        #'backend': 'PDF',
        'font.size': 12,
        'figure.figsize': (4,3),
        'figure.dpi': 100.0,
        'figure.subplot.left': 0.20,
        'figure.subplot.right': 0.97,
        'figure.subplot.bottom': 0.20,
        'figure.subplot.top': 0.90,
        #'grid.color': '0.1',
        #'grid.linestyle': ':',
        #'grid.linewidth': 0.5,
        #'axes.grid' : True,
        #'axes.grid.which' : 'both',
        #'axes.grid.axis' : 'y',
        'axes.axisbelow': True,
        'axes.titlesize' : 'x-small',
        'axes.labelsize' : 12,
        'axes.formatter.limits': (-4,4),
        'xtick.labelsize' : 10,#get_tick_font_size_10(),
        'ytick.labelsize' : 10, #get_tick_font_size_10(),
        'lines.linewidth' : 2.0,
        'lines.markeredgewidth' : 0.5,
        'lines.markersize' : 10,
        'legend.fontsize' : 10,
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
