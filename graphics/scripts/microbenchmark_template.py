import argparse

import pandas as pds
import seaborn as sns
import matplotlib.pyplot as plt

LOOPS = ['Lecture',  'Écriture', 'Calcul']

def make_point(loop, time, angle=False):
    return {'loop': loop, 'iteration': time, 'angle': angle}

def make_sequence_rcw(read, write, compute, length):
    loops = [0, 2, 1]
    loop_counters = [read, write, compute]
    i = 0
    ret = []
    prev_loop = None
    while True:
        for loop in loops:
            if prev_loop is not None:
                ret.append(make_point(prev_loop, i, angle=True))
            prev_loop = loop
            
            counter = loop_counters[loop]
            while counter > 0:
                ret.append(make_point(loop, i))
                counter -= 1
                length -= 1
                i += 1
                if length <= 0:
                    return ret 

def make_sequence_rcwc(read, write, compute, length):
    loops = [0, 2, 1, 2]
    loop_counters = [read, write, compute]
    i = 0
    ret = []
    prev_loop = None
    while True:
        for loop in loops:
            if prev_loop is not None:
                ret.append(make_point(prev_loop, i, angle=True))
            prev_loop = loop

            counter = loop_counters[loop]
            while counter > 0:
                ret.append(make_point(loop, i))
                counter -= 1
                length -= 1
                i += 1
                if length <= 0:
                    return ret

def plot(sequence, dst):
    df = pds.DataFrame(sequence[:-1])

    length = df.iteration.max()
    signal_line_style = {'ls': '--', 'linewidth': 1, 'color': 'lightgray'}

    plt.figure(figsize=(6.4, 3))

    plt.axhline(0, 0, 1, **signal_line_style)
    plt.axhline(1, 0, 1, **signal_line_style)
    plt.axhline(2, 0, 1, **signal_line_style)
    
    plt.plot(df.iteration, df.loop, color='gray', linewidth=3)
    plt.scatter(df[~df.angle].iteration, df[~df.angle].loop, color='gray')
    plt.yticks([0, 1,2], LOOPS)
    plt.xticks([x for x in range(length + 1)if (x % 2) == 0])
    plt.tick_params(axis='y', width=0, labelsize=18)

    sns.despine(left=True)
    plt.xlim((-0.5, length + 1))

    plt.savefig(dst, bbox_inches="tight")

templates = {'rcw': make_sequence_rcw, 'rcwc': make_sequence_rcwc}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("template")
    parser.add_argument("read", type=int)
    parser.add_argument("write", type=int)
    parser.add_argument("compute", type=int)
    parser.add_argument("length", type=int)
    parser.add_argument("out")

    args = parser.parse_args()

    plot(templates[args.template](args.read, args.write, args.compute, args.length),args.out)
