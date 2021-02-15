#!/usr/bin/python

import sys
import logging

import matplotlib
matplotlib.use('Agg') # for systems without X11
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_pdf import PdfPages

from plot_common import *

STATS_FILENAME = "figure2_stats.txt"

# https://metrics.torproject.org/reproducible-metrics.html#performance

def main():
    args = get_args()
    setup_logging(args.logfile)
    run(args)
    logging.info("All done!")

def load_tor_goodput(path):
    goodputs = []
    with open(path, 'r') as inf:
        for line in inf:
            if '201' == line[0:3]:
                gput = line.strip().split(',')[2]
                if len(gput) > 0:
                    goodputs.append(float(gput))
    return goodputs

def get_tor_error_rates(data):
    err_rates = []
    for day in data:
        year = int(day.split('-')[0])
        month = int(day.split('-')[1])

        total = int(data[day]['requests'])
        if total <= 0:
            continue

        timeouts = int(data[day]['timeouts'])
        failures = int(data[day]['failures'])

        # the hong kong onionperf infrastucture had an error
        # https://metrics.torproject.org/torperf-failures.html?start=2019-06-01&end=2019-08-31&server=public
        if timeouts > 100 and year == 2019 and month in [6, 7, 8]:
            continue
        if timeouts > 100 and year == 2018 and month in [1, 5, 6, 7, 12]:
            continue

        err_rates.append((timeouts+failures)/float(total)*100.0)
    return err_rates

def load_tor_results(args, bw_filename, torperf_filename):
    torperf = load_json(f"{args.inpath}/tor/{torperf_filename}")

    tor = {
        'netgput': load_tor_goodput(f"{args.inpath}/tor/{bw_filename}"),
        'ttfb': None,
        'ttlb': torperf["download_times"],
        'err': get_tor_error_rates(torperf["daily_counts"]),
        'rtt': torperf["circuit_rtt"],
        'cbt': torperf["circuit_build_times"],
        'clientgput': [t/1000000 for t in torperf["throughput"]],
    }

    return tor

def load_shadow_goodput(path):
    goodputs = []
    data = load_json(path)

    # extrapolate from 31% to 100% network
    scale = 1.0/0.31

    for secstr in data:
        gbits = int(data[secstr])/1024.0/1024.0/1024.0*8.0
        goodputs.append(gbits*scale)

    return goodputs

def get_shadow_download_gput(ttfb, ttlb):
    gput = []

    # Tor computs gput based on the time between the .5 MiB byte to the 1 MiB byte.
    # Ie to cut out circuit build and other startup costs. Since tgen doesn't have a
    # timestamp for .5MiB on each download, we instead cut out the ttfb.
    # https://metrics.torproject.org/reproducible-metrics.html#performance
    mean_ttfb_1m = mean(ttfb['1048576'])
    for seconds in ttlb["1048576"]:
        gput_sec = seconds - mean_ttfb_1m
        if gput_sec <= 0: continue
        mbit_per_second = 1048576.0/1048576.0*8.0/gput_sec
        gput.append(mbit_per_second)

    mean_ttfb_5m = mean(ttfb['5242880'])
    for seconds in ttlb["5242880"]:
        gput_sec = seconds - mean_ttfb_5m
        if gput_sec <= 0: continue
        mbit_per_second = 5242880.0/1048576.0*8.0/gput_sec
        gput.append(mbit_per_second)

    return gput

def load_shadow_results(args, exp_dir):
    shadow = {
        'netgput': load_shadow_goodput(f"{args.inpath}/{exp_dir}/oniontrace_tput.json"),
        'ttfb': load_json(f"{args.inpath}/{exp_dir}/time_to_first_byte_recv.json"),
        'ttlb': load_json(f"{args.inpath}/{exp_dir}/time_to_last_byte_recv.json"),
        'err': load_json(f"{args.inpath}/{exp_dir}/error_rate.json")["ALL"],
        'rtt': load_json(f"{args.inpath}/{exp_dir}/round_trip_time.json"),
        'cbt': None,
        'clientgput': None,
    }

    shadow['clientgput'] = get_shadow_download_gput(shadow['ttfb'], shadow['ttlb'])

    cbt_path = f"{args.inpath}/{exp_dir}/oniontrace_perfclient_cbt.json"
    if os.path.exists(cbt_path):
        shadow_cbt_over_time = load_json(cbt_path)
        shadow['cbt'] = []
        for secstr in shadow_cbt_over_time:
            shadow['cbt'].extend(shadow_cbt_over_time[secstr])

    return shadow

def get_shadow_data_subset(shadow_100, key1, key2=None):
    if key2 != None:
        return {i: shadow_100[i][key1][key2] for i in shadow_100}
    else:
        return {i: shadow_100[i][key1] for i in shadow_100}

def run(args):
    logging.info("Loading data")

    tor_2018 = load_tor_results(args, "bandwidth-2018-01-01-2018-12-31.csv", "torperf-2018.json.xz")
    tor_2019 = load_tor_results(args, "bandwidth-2019-01-01-2019-12-31.csv", "torperf-2019.json.xz")

    #shadow_100 = load_shadow_results(args, "shadowtor-1.0-1-1.0-seed1")
    shadow_31_ccs18 = load_shadow_results(args, "shadowtor-0.31-ccs2018")
    #shadow_31_new = load_shadow_results(args, "shadowtor-0.30795-a-1.0-seed1")
    shadow_31_new = {i: load_shadow_results(args, f"shadowtor-0.31-{i}-1.0-seed1") for i in range(1,11)}

    #---
    if os.path.exists(STATS_FILENAME):
        os.remove(STATS_FILENAME)

    #---
    logging.info("Starting to plot")
    set_plot_options()
    matplotlib.rcParams['ytick.major.pad']='0.0'

    plot(tor_2019['ttlb']["51200"],
        get_shadow_data_subset(shadow_31_new, 'ttlb', '51200'),
        tor_2018['ttlb']['51200'],
        shadow_31_ccs18['ttlb']['51200'],
        "figure2e.pdf", xlabel="Time (sec)")#, ylabel="CDF")

    plot(tor_2019['ttlb']["1048576"],
        get_shadow_data_subset(shadow_31_new, 'ttlb', '1048576'),
        tor_2018['ttlb']['1048576'],
        shadow_31_ccs18['ttlb']['1048576'],
        "figure2f.pdf", xlabel="Time (sec)")

    plot(tor_2019['ttlb']["5242880"],
        get_shadow_data_subset(shadow_31_new, 'ttlb', '5242880'),
        tor_2018['ttlb']['5242880'],
        shadow_31_ccs18['ttlb']['5242880'],
        "figure2g.pdf", xlabel="Time (sec)")

    plot(tor_2019['clientgput'],
        get_shadow_data_subset(shadow_31_new, 'clientgput'),
        tor_2018['clientgput'],
        shadow_31_ccs18['clientgput'],
        "figure2d.pdf", xlabel="Goodput (Mbit/s)      .")

    plot(tor_2019["cbt"],
        get_shadow_data_subset(shadow_31_new, 'cbt'),
        tor_2018['cbt'],
        shadow_31_ccs18['cbt'],
        "figure2a.pdf", xlabel="Time (sec)")#, ylabel="CDF")

    plot(tor_2019["rtt"],
        get_shadow_data_subset(shadow_31_new, 'rtt'),
        tor_2018['rtt'],
        shadow_31_ccs18['rtt'],
        "figure2b.pdf", xlabel="Time (sec)")

    plot(tor_2019['err'],
        get_shadow_data_subset(shadow_31_new, 'err'),
        tor_2018['err'],
        shadow_31_ccs18['err'],
        "figure2c.pdf", xlabel="Error Rate (\%)", xscale="log", xmax=200)

    plot(tor_2019['netgput'],
        get_shadow_data_subset(shadow_31_new, 'netgput'),
        tor_2018['netgput'],
        shadow_31_ccs18['netgput'],
        "figure2h.pdf", xlabel="Goodput (Gbit/s)")

    #---
    # dump the legend
    pyplot.figure()
    lines = [
        pyplot.plot([0], [0], linestyle='-', color="C0")[0],
        #pyplot.plot([0], [0], linestyle='--', color="C1")[0],
        (pyplot.plot([0], [0], linestyle='--', color="C1")[0], pyplot.fill(0, 0, color="C1", alpha=0.5)[0]),
        pyplot.plot([0], [0], linestyle='-.', color="C2")[0],
        pyplot.plot([0], [0], linestyle=':', color="C3")[0],
    ]
    labels = ["Tor 2019", "This Work (s=0.31)", "Tor 2018", "CCS 2018 (s=0.31)"]
    f = pyplot.figure(figsize=(5.25,.3))
    f.legend(lines, labels, ncol=4, loc='center')
    f.tight_layout(pad=0.3)
    f.savefig("figure2_legend.pdf")

    f = pyplot.figure(figsize=(.25,1.75))
    f.text(0.25, 0.8, 'CDF', rotation='vertical')
    f.tight_layout(pad=0.3)
    f.savefig("figure2_ylabel.pdf")

def plot(tor_2019, shadow_31_new, tor_2018, shadow_31_ccs18, filename, xlabel=None, ylabel=None, xscale=None, xmax=None):
    fig = pyplot.figure()

    log_stats(STATS_FILENAME, f"{filename}: Tor 2019: ", tor_2019)
    x, y = getcdf(tor_2019, shownpercentile=0.99)
    x = [getfirstorself(item) for item in x]
    pyplot.plot(x, y, linestyle='-', color='C0')

    log_stats(STATS_FILENAME, f"{filename}: Tor 2018: ", tor_2018)
    x, y = getcdf(tor_2018, shownpercentile=0.99)
    x = [getfirstorself(item) for item in x]
    pyplot.plot(x, y, linestyle='-.', color="C2")

    if shadow_31_new is not None:
        for i in shadow_31_new:
            log_stats(STATS_FILENAME, f"{filename}: Shadow 31\%: {i}:", shadow_31_new[i])
        #x, y = getcdf(shadow_31_new, shownpercentile=0.99)
        #x = [getfirstorself(item) for item in x]
        #pyplot.plot(x, y, linestyle='--', color='C1')
        draw_cdf_ci(shadow_31_new, None, pyplot, levels=[10], colors=["C1"], linestyle='--')

    if shadow_31_ccs18 is not None:
        log_stats(STATS_FILENAME, f"{filename}: CCS'18 31\%: ", shadow_31_ccs18)
        x, y = getcdf(shadow_31_ccs18, shownpercentile=0.99)
        x = [getfirstorself(item) for item in x]
        pyplot.plot(x, y, linestyle=':', color='C3')

    if xscale is not None:
        pyplot.xscale(xscale)
        pyplot.xticks([1.0, 10.0, 100.0])
    else:
        fig.axes[0].xaxis.set_major_locator(pyplot.MaxNLocator(3))

    if xmax is not None:
        pyplot.xlim(xmax=xmax)
    if xlabel is not None:
        pyplot.xlabel(xlabel)
    if ylabel is not None:
        pyplot.ylabel(ylabel)

    pyplot.tight_layout(pad=0.3)
    pyplot.savefig(filename)

def set_plot_options():
    options = {
        #'backend': 'PDF',
        'font.size': 12,
        'figure.figsize': (1.25,1.75),
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
        'axes.labelsize' : 10,
        'axes.formatter.limits': (-4,4),
        'xtick.labelsize' : 8,#get_tick_font_size_10(),
        'ytick.labelsize' : 8,#get_tick_font_size_10(),
        'lines.linewidth' : 2.0,
        'lines.markeredgewidth' : 0.5,
        'lines.markersize' : 10,
        'legend.fontsize' : 10,
        'legend.fancybox' : False,
        'legend.shadow' : False,
        'legend.borderaxespad' : 0.5,
        'legend.columnspacing' : 1.0,
        'legend.numpoints' : 1,
        'legend.handletextpad' : 0.25,
        'legend.handlelength' : 2.0,
        'legend.labelspacing' : .25,
        'legend.markerscale' : 1.0,
        # turn on the following to embedd fonts; requires latex
        'ps.useafm' : True,
        'pdf.use14corefonts' : True,
        'text.usetex' : True,
        #'text.latex.preamble': r'\boldmath',
        'text.latex.preamble': r'\usepackage{amsmath}',
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
