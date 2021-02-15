import sys
import os
import logging
import json
import subprocess

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from scipy.stats import scoreatpercentile as score, t
from numpy import mean, median, std, arange, isnan, log10, quantile, sqrt, linspace, var

def get_tick_font_size_30():
    return 7

def get_tick_font_size_10():
    return 8

def get_boxplot_whiskers():
    # whis=1.5 (the default) shows the tukey boxplot, where the whiskers extend to 1.5*IQR
    # whis='range' shows min and max
    # whis=[5, 95] extends the lower to the 5th percentile and the upper to the 95th
    return [0,99]

def get_net_scale(filepath):
    parts = filepath.split('/')
    for p in parts:
        # eg shadowtor-0.3-a-0.8-seed2
        if "shadowtor-" in p:
            parts2 = p.split('-')
            return parts2[1]

def get_net_instance(filepath):
    parts = filepath.split('/')
    for p in parts:
        # eg shadowtor-0.3-a-0.8-seed2
        if "shadowtor-" in p:
            parts2 = p.split('-')
            return "{}-{}".format(parts2[1], parts2[2])

def get_net(filepath):
    parts = filepath.split('/')
    for p in parts:
        # eg shadowtor-0.3-a-0.8-seed2
        if "shadowtor-" in p:
            parts2 = p.split('-')
            return parts2[2]

def get_load_percentage(filepath):
    parts = filepath.split('/')
    for p in parts:
        # eg shadowtor-0.3-a-0.8-seed2
        if "shadowtor-" in p:
            parts2 = p.split('-')
            return parts2[3]

def get_seed(filepath):
    parts = filepath.split('/')
    for p in parts:
        # eg shadowtor-0.3-a-0.8-seed2
        if "shadowtor-" in p:
            parts2 = p.split('-')
            return parts2[4][-1]

def get_filepaths(data_path, filename_key): # e.g. key='tgen.analysis.json'
    stats = []
    for root, dirs, files in os.walk(data_path, followlinks=True):
        for name in files:
            if filename_key in name:
                p = os.path.join(root, name)
                logging.info("Found {}".format(p))
                stats.append(p)
    return stats

def draw_hist(db, bytes, axis, quantiles_to_plot=[0.5], colors=["C0"], linestyle="-", label_prefix=""):
    quantile_buckets = {q:[] for q in quantiles_to_plot}

    # we should have one empirical value for each simulation for each quantile
    for sim in sorted(db.keys()):
        dl_times = db[sim][bytes] if bytes != None else db[sim]
        dl_times = [getfirstorself(item) for item in dl_times]
        dl_times.sort()
        num_times = len(dl_times)
        for q in quantile_buckets:
            # interpolation method to use when the desired quantile lies between two data points
            val_at_q = dl_times[int((num_times-1) * q)]
            quantile_buckets[q].append(val_at_q)

    for i, q in enumerate(quantile_buckets):
        bucket = quantile_buckets[q]
        axis.hist(bucket, density=False, histtype='step',
            label=f"{label_prefix}p{q*100}",
            color=colors[i%len(colors)],
            linestyle=linestyle)

def draw_cdf_range(db, bytes, axis, color="C0", linestyle="-", label_prefix=""):
    range_data = {}

    for net in sorted(db.keys()):
        x, y = getcdf(db[net][bytes]) if bytes != None else getcdf(db[net])
        x = [getfirstorself(item) for item in x]
        for i, val in enumerate(y):
            y_bucket_key = min(0.99999, round(val, 2)) # avoid polygon plot issue in fill_betweenx
            if y_bucket_key > 0.99: continue # avoid xlim bug
            range_data.setdefault(y_bucket_key, []).append(x[i])

    y = sorted(range_data.keys())

    axis.fill_betweenx(y,
        [score(range_data[i], 0) for i in y],
        [score(range_data[i], 100) for i in y],
        label=f"{label_prefix}[P0,P100]", color=color, alpha=0.25, linestyle=linestyle)
    axis.fill_betweenx(y,
        [score(range_data[i], 25) for i in y],
        [score(range_data[i], 75) for i in y],
        label=f"{label_prefix}[P25,P75]", color=color, alpha=0.5, linestyle=linestyle)
    axis.plot([score(range_data[i], 50) for i in y], y, label=f"{label_prefix}P50", color=color, linestyle=linestyle)

def get_err_factor(k, confidence):
    return t.ppf(confidence/2 + 0.5, k-1)/sqrt(k-1)

def draw_cdf_ci(db, bytes, axis, levels=[2], colors=["C0"], confidence=0.95, linestyle="-", label_prefix=""):
    quantiles_to_plot = list(linspace(0, 0.99, num=1000))

    for l, level in enumerate(sorted(levels)):
        quantile_buckets = {q:[] for q in quantiles_to_plot}

        # we should have one empirical value for each simulation for each quantile
        for sim in sorted(db.keys())[0:level]:
            dl_times = db[sim][bytes] if bytes != None else db[sim]
            dl_times.sort(key=getfirstorself)
            num_times = len(dl_times)
            if num_times == 0:
                continue
            for q in quantile_buckets:
                val_at_q = dl_times[int((num_times-1) * q)]
                quantile_buckets[q].append(val_at_q)

        if len(quantile_buckets[0]) < level:
            level = len(quantile_buckets[0])

        z = get_err_factor(level, confidence)
        x, x_left, x_right = [], [], []
        for i, q in enumerate(quantiles_to_plot):
            bucket = quantile_buckets[q]

            # bucket will be a list of items, each of which will either
            # be the value (a number), or a list of two numbers (the
            # value and the resolution).  If it's just a value, the
            # correspinding resolution is 0.  Create the list of values
            # and the list of resolutions.
            emp_sample = [getfirstorself(item) for item in bucket]
            resolutions = [getsecondorzero(item) for item in bucket]

            # The resolution variance is 1/12 of the sum of the squares
            # of the resolutions
            resolution_variance = sum([res**2 for res in resolutions])/12

            k, m, v = len(emp_sample), mean(emp_sample), var(emp_sample)
            s = sqrt(v + resolution_variance/k)
            assert k == level

            x_left_val = m-z*s
            x_right_val = m+z*s

            x.append(m)
            x_left.append(max(0, x_left_val))
            x_right.append(x_right_val)

        # for debugging
        #axis.plot(x_left, y, label=f"level={level}", color=colors[l%len(colors)], linestyle=linestyle)
        #axis.plot(x_right, y, label=f"level={level}", color=colors[l%len(colors)], linestyle=linestyle)

        color_spec = colors[l%len(colors)]

        if len(levels) == 1:
            alpha_spec = 0.5
        else:
            alpha_spec = 0.6/len(levels)*(l+1)

        label_suffix = f"{level}"
        if level == 97 or level == 99: # 100% error rate fixup
            label_suffix = "100"

        y = quantiles_to_plot
        #y = [1-q for q in quantiles_to_plot] #ccdf
        if l == len(levels)-1:
            axis.plot(x, y, linestyle=linestyle, color=color_spec)
        axis.fill_betweenx(y, x_left, x_right,
            #step='mid',
            label=f"{label_prefix}$n$={label_suffix}",
            color=color_spec,
            alpha=alpha_spec,
            linestyle='-')

def draw_cdf(axis, data, labels,
        colors=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11'],
        linestyles=['-', ':', '--', '-.']):

    for i, d in enumerate(data):
        x, y = getcdf(d)
        x = [getfirstorself(item) for item in x]
        axis.plot(x, y, label=labels[i], color=colors[i], linestyle=linestyles[i])

    #axis.set_xticklabels(labels, ha='center', fontsize=get_tick_font_size()) # rotation=60,
    for tick in axis.yaxis.get_major_ticks():
        tick.label.set_fontsize(get_tick_font_size_10())

    axis.xaxis.label.set_size(get_tick_font_size_10())

    axis.legend(loc='best')

def draw_boxplot(axis, data, labels, rotation=0, tick_fontsize=8):
    # whis=1.5 (the default) shows the tukey boxplot, where the whiskers extend to 1.5*IQR
    # whis='range' shows min and max
    # whis=[5, 95] extends the lower to the 5th percentile and the upper to the 95th
    box = axis.boxplot(data, patch_artist=True, labels=labels, whis=get_boxplot_whiskers(), showfliers=True, showmeans=True, meanprops={'markersize':3, 'markeredgecolor':'black', 'markerfacecolor':'black'}, medianprops={'color':'black'}, flierprops={'markersize':0.5, 'markeredgecolor':'black', 'markerfacecolor':'black'})

    colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    axis.set_xticklabels(labels, rotation=rotation, ha='center', fontsize=tick_fontsize)
    for tick in axis.yaxis.get_major_ticks():
        tick.label.set_fontsize(tick_fontsize)

    axis.xaxis.label.set_size(tick_fontsize)

    axis.grid(b=False)
    axis.grid(axis='y')

    return box

## helper - cumulative fraction for y axis
def cf(d): return arange(1.0,float(len(d))+1.0)/float(len(d))

## helper - if the passed item is a list, return its first
## element; otherwise, return the item itself
def getfirstorself(item):
    if isinstance(item, list):
        return item[0]
    return item

## helper - if the passed item is a list, return its second
## element; otherwise, return 0
def getsecondorzero(item):
    if isinstance(item, list):
        return item[1]
    return 0

## helper - return step-based CDF x and y values
## only show to the 99th percentile by default
def getcdf(data, shownpercentile=1.0, maxpoints=100000.0):
    # data will be a list of items which are either numbers or
    # lists of numbers; sort by the first element in the list if it's a
    # list, or by the number itself if it's a number
    data.sort(key=getfirstorself)
    frac = cf(data)
    k = len(data)/maxpoints
    x, y, lasty = [], [], 0.0
    for i in range(int(round(len(data)*shownpercentile))):
        if i % k > 1.0: continue
        assert not isnan(data[i]).any()
        x.append(data[i])
        y.append(lasty)
        x.append(data[i])
        y.append(frac[i])
        lasty = frac[i]
    return x, y

def log_stats(filename, msg, dist):
    #from numpy import mean, median, std
    #from scipy.stats import scoreatpercentile as score
    b = sorted(dist)#.values()
    b = [getfirstorself(item) for item in b]
    with open(filename, 'a') as outf:
        print(msg, file=outf)
        print("min={} q1={} median={} q3={} max={} mean={} stddev={}".format(min(b), score(b, 25), median(b), score(b, 75), max(b), mean(b), std(b)), file=outf)

def load_json(data_path):
    filename = os.path.abspath(os.path.expanduser(data_path))
    if filename.endswith(".xz"):
        xzcatp = subprocess.Popen(["xzcat", filename], stdout=subprocess.PIPE)
        data = json.load(xzcatp.stdout)
    else:
        with open(filename, 'r') as fin:
            data = json.load(fin)
    return data

def setup_logging(logfilename=None):
    my_handlers = []

    stdout_handler = logging.StreamHandler(sys.stdout)
    my_handlers.append(stdout_handler)

    if logfilename != None:
        file_handler = logging.FileHandler(filename=logfilename)
        my_handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(created)f [plot] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=my_handlers,
    )

    msg = "Logging system initialized! Logging events to stdout"
    if logfilename != None:
        msg += " and to '{}'".format(logfilename)
    logging.info(msg)

def get_args():
    parser = ArgumentParser(
            description='Extract plot data from tgen analysis json files',
            formatter_class=CustomHelpFormatter)

    parser.add_argument('-l', '--logfile', help="Name of the file to store log output in addition to stdout", metavar="PATH", default="plot.log")
    parser.add_argument('-i', '--inpath', help="Path to a directory containing plot data output by extractor", metavar="PATH", default="plot_data")

    args = parser.parse_args()
    return args

class CustomHelpFormatter(ArgumentDefaultsHelpFormatter):
    # adds the 'RawDescriptionHelpFormatter' to the ArgsDefault one
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

import numpy as np
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator


class TailLog(mscale.ScaleBase):
    name = 'taillog'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self, axis)
        self.nines = kwargs.get('nines', 2)

    def get_transform(self):
        return self.Transform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        # axis.set_major_locator(FixedLocator(
        #         np.array([1-10**(-k) for k in range(1+self.nines)])))
        # axis.set_major_formatter(FixedFormatter(
        #         [str(1-10**(-k)) for k in range(1+self.nines)]))

        #majloc = [10**(-1*self.nines)*k for k in range(100) if k >= 90 or k % 10 == 0]
        majloc = [0.0, 0.9, 0.99]
        majloc = [round(k, self.nines) for k in majloc]
        axis.set_major_locator(FixedLocator(
                np.array(majloc)))
        axis.set_major_formatter(FixedFormatter(
                [str(k) for k in majloc]))

        minloc = [10**(-1*self.nines)*k for k in range(100) if k not in [0, 90, 99] and (k > 90 or k % 10 == 0)]
        minloc = [round(k, self.nines) for k in minloc]
        axis.set_minor_locator(FixedLocator(
                np.array(minloc)))
        axis.set_minor_formatter(FixedFormatter(
                [str(k) for k in minloc]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min(1 - 10**(-self.nines), vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > 1-10**(-1-self.nines), a)
            if masked.mask.any():
                return -ma.log10(1-a)
            else:
                return -np.log10(1-a)

        def inverted(self):
            return TailLog.InvertedTransform(self.nines)

    class InvertedTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            return 1. - 10**(-a)

        def inverted(self):
            return TailLog.Transform(self.nines)

mscale.register_scale(TailLog)
