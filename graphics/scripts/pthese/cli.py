import argparse
import numpy as np
import matplotlib.pyplot as plt

class CLIPlots():
    def __init__(self):
        self._register = {}
        self._arg_parser = self.__init_argparser()

    def __init_argparser(self):
        parser =  argparse.ArgumentParser()

        parser.add_argument('--out', '-o')
        parser.add_argument('--plot', default='default')

        return parser

    def cli_plot(self, name):

        def __w1(fn):
            self._register[name] = fn
            # print(self._register)

            def __w2(*args, **kwargs):
                return fn(*args, **kwargs)
            return __w2

        return __w1

    def run(self):
        args = self._arg_parser.parse_args()

        self._register[args.plot](args)

        if not args.out:
            plt.show()
        else:
            plt.savefig(args.out, bbox_inches='tight')

