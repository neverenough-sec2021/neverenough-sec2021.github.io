#!/usr/bin/env python

import sys

import matplotlib
import matplotlib.pyplot as pyplot

from random import sample
from numpy import isnan, arange, std, mean, sqrt, quantile
from scipy.stats import t, norm

def get_err_factor(k, ci_level=0.95):
    return t.ppf(ci_level/2 + 0.5, k-1)/sqrt(k-1)

def get_cdf_val(q, loc=0, scale=1):
    return abs(norm.ppf(q, loc=loc, scale=scale))

FONT_SIZE="10.0"
FONT_WEIGHT="bold"

def main():
    set_plot_options()

    y = [(i+1)/100.0 for i in list(range(100))]
    x1 = [get_cdf_val(q, loc=10, scale=1) for q in y]
    x2 = [get_cdf_val(q, loc=15, scale=5) for q in y]
    x3 = [get_cdf_val(q, loc=20, scale=2.5) for q in y]

    fig = pyplot.figure()

    pyplot.plot(x1, y, ls='-', label="$\widehat{F}_{X1}$")
    pyplot.plot(x2, y, ls='--', label="$\widehat{F}_{X2}$")
    pyplot.plot(x3, y, ls=':', label="$\widehat{F}_{X3}$")

    chosen_color = "purple"
    def draw_arrow(xloc, yloc, showtext=True):
        pyplot.annotate(r"$\boldsymbol{\widehat{F}_{Xi}^{-1}(.5)}$",
            xy=(xloc, yloc),
            xytext=(21, .1),
            verticalalignment='center',
            fontsize=FONT_SIZE,
            fontweight=FONT_WEIGHT,
            color=chosen_color,
            alpha=1.0 if showtext else 0.0,
            arrowprops=dict(width=1, headwidth=8, headlength=4, color=chosen_color, shrink=0.03))

    draw_arrow(x1[50], y[50], True)
    draw_arrow(x2[50], y[50], False)
    draw_arrow(x3[50], y[50], False)

    pyplot.xlim(xmin=-2, xmax=32)

    pyplot.xlabel("Random Variable $X$")
    pyplot.ylabel(f"Empirical CDF")

    pyplot.legend(loc="upper left")
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("figure4a.pdf")


    fig = pyplot.figure()

    y = y[0:-2]
    z = get_err_factor(3) # t dist for n=3 networks
    x, x_left, x_right = [], [], []
    for i, q in enumerate(y):
        emp_vals = [x1[i], x2[i], x3[i]]
        m, s = mean(emp_vals), std(emp_vals)
        x.append(m)
        x_left.append(m-z*s)
        x_right.append(m+z*s)

    pyplot.plot(x, y, ls='-', color='k', label=r"$\mu \approx F_{X}^{-1}$")
    pyplot.fill_betweenx(y, x_left, x_right,
        #step='mid',
        label="CI",
        alpha=0.4,
        color='k',
        linestyle='-')

    pyplot.annotate(r"$\boldsymbol{\mu(.5)}$",
        xy=(x[50], y[50]),
        xytext=(1, .1),
        verticalalignment='center',
        fontsize=FONT_SIZE,
        fontweight=FONT_WEIGHT,
        color=chosen_color,
        alpha=1.0,
        arrowprops=dict(width=1, headwidth=8, headlength=4, color=chosen_color, shrink=0.03))

    chosen_color = "darkred"
    pyplot.annotate(r"$\boldsymbol{\mu(.5)-\epsilon(.5)}$",
        xy=(x_left[50], y[50]),
        xytext=(-5, .85),
        verticalalignment='center',
        fontsize=FONT_SIZE,
        fontweight=FONT_WEIGHT,
        color=chosen_color,
        alpha=1.0,
        arrowprops=dict(width=1, headwidth=8, headlength=4, color=chosen_color, shrink=0.03))
    pyplot.annotate(r"$\boldsymbol{\mu(.5)+\epsilon(.5)}$",
        xy=(x_right[50], y[50]),
        xytext=(20, .85),
        verticalalignment='center',
        fontsize=FONT_SIZE,
        fontweight=FONT_WEIGHT,
        color=chosen_color,
        alpha=1.0,
        arrowprops=dict(width=1, headwidth=8, headlength=4, color=chosen_color, shrink=0.03))

    pyplot.xlabel("Random Variable $X$")
    pyplot.ylabel(f"Estimated True CDF")

    pyplot.legend(loc="lower right")
    pyplot.tight_layout(pad=0.3)

    pyplot.savefig("figure4b.pdf")

def set_plot_options():
    options = {
        #'backend': 'PDF',
        'font.size': 12,
        'figure.figsize': (3,2),
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
        'axes.labelsize' : 12,
        'axes.formatter.limits': (-4,4),
        'xtick.labelsize' : 10,#get_tick_font_size_10(),
        'ytick.labelsize' : 10,#get_tick_font_size_10(),
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
