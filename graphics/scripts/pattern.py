import pandas as pds
#import seaborn as sns
import matplotlib.pyplot as plt
import random
import numpy as np
import itertools

import argparse

import pthese.cli

cp = pthese.cli.CLIPlots()

def do_plot(x, y):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=300)

    ax.scatter(x,y, s=1, color='blue', marker=',', alpha=0.6)
    ax.set_ylim((-5, 275))
    ax.set_xticks([0, 16 << 10, 32 << 10, 48 << 10, 64 << 10])
    ax.set_yticks([0, 64, 128, 192, 256])
    ax.set_xlabel("Instructions exécutées")
    ax.set_ylabel("Sauts")
    #   print(x, y)
    # fig.savefig(out, bbox_inches='tight')

def random_pattern(x):
    return [random.randint(0, 256) for val in x]

# def strides(x, values):
#     y = [b for a, b in zip(x, itertools.cycle(values))]
#     do_plot(x, y)

def interleave(*args):
    return [x for t in zip(*args) for x in t]

def interleave_patterns(x, *ys):
    return [b for a, b in zip(x, itertools.cycle((interleave(*ys))))]

def do_make_x(start, end, step):
    return np.linspace(start, end, int((end-start) / step))

def make_x(cli_args):
    return do_make_x(0, 64 << 10, cli_args.step)

@cp.cli_plot('linear-pattern')
def plot_linear_pattern(cli_args):
    x = make_x(cli_args)

    return do_plot(x, interleave_patterns(x, [128]))

# @cp.cli_plot('strided-pattern')
# def plot_strided_pattern(cli_args):
#     x = make_x(cli_args)
#
#     return strides(x, [64, 128, 192, 256])

@cp.cli_plot('random-pattern')
def plot_random_pattern(cli_args):
    x = make_x(cli_args)
    y = random_pattern(x)

    do_plot(x, y)


@cp.cli_plot('strided-pattern-2')
def plot_strided_2(cli_args):
    x = make_x(cli_args)
    strides = [64, 128, 192, 256]
    y = interleave_patterns(x, strides)

    do_plot(x, y)

@cp.cli_plot('quad-pattern')
def plot_quad(cli_args):
    xs = make_x(cli_args)
    slope = cli_args.slope

    y = [(slope * i) % 256 for i, x in enumerate(xs)]

    do_plot(xs, y)

@cp.cli_plot('strided-quad-pattern')
def plot_quad(cli_args):
    xs = make_x(cli_args)
    slope = cli_args.slope

    ys = [[slope * i % 256 for i, x in enumerate(xs)],
          [(slope * i + 64) % 256 for i, x in enumerate(xs)]]
    y = interleave_patterns(xs, *ys)

    do_plot(xs, y)

@cp.cli_plot('composed-pattern')
def plot_composed(cli_args):
    xs = make_x(cli_args)

    y3 = [0.75 * i % 256 for i, x in enumerate(xs)]
    y1 = [-0.75 * i % 256 for i, x in enumerate(xs)]
    y2 = random_pattern(xs)

    do_plot(xs, interleave_patterns(xs, y1, y2, y3))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    #
    # parser.add_argument('pattern')
    # parser.add_argument('step', type=int)
    # parser.add_argument('output')
    #
    # args = parser.parse_args()
    # out = args.output
    #
    #
    # x = make_x(0, 64 << 10, args.step)
    #
    # print(args.pattern, len(x))
    #
    # if args.pattern == 'linear':
    #     strides(x, [128], out)
    # elif args.pattern == 'strided':
    #     strides(x, [64, 128, 192, 256], out)
    # elif args.pattern == 'quad':
    #     str
    # else:
    #     random_pattern(x, out)

    cp._arg_parser.add_argument('--step', type=int, default=10)
    cp._arg_parser.add_argument('--slope', type=float, default=0.5)

    cp.run()
