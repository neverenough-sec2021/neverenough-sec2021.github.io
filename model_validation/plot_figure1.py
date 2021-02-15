#!/usr/bin/env python

import sys
import json
import lzma
import datetime

import matplotlib
import matplotlib.pyplot as pyplot

def main():
    set_plot_options()

    with lzma.open("data/tor/relay-churn.json.xz", 'r') as inf:
        churn = json.load(inf)

    x_time, y_relays_remaining, y_relays_joined = [], [], []

    last_ts = 0.0
    for i, ts_str in enumerate(sorted(churn.keys())):
        ts = float(ts_str)
        assert(ts > last_ts)
        last_ts = ts

        dt = datetime.datetime.fromtimestamp(ts)
        x_time.append(dt)

        relays_now = set(churn[ts_str])

        if i == 0:
            remain = relays_now
            join = set()
        else:
            for fp in relays_now:
                if fp not in remain:
                    join.add(fp)
            remain = remain & relays_now

        y_relays_joined.append(len(join))
        y_relays_remaining.append(len(remain))

    pyplot.figure()

    pyplot.plot(x_time, y_relays_remaining, ls='-', label='Remaining from 2019-01-01')
    pyplot.plot(x_time, y_relays_joined, ls='--', label='Newly Joined since 2019-01-01')

    #pyplot.xlabel("Date")
    pyplot.ylabel("Relay Count")
    pyplot.xticks(rotation=25, ha="right")

    pyplot.legend(loc="lower right")
    pyplot.tight_layout(pad=0.3)
    pyplot.savefig("figure1.pdf")


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
        'xtick.labelsize' : 8,#get_tick_font_size_10(),
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
