import pandas as pds
import matplotlib.pyplot as plt
import seaborn as sns

from pthese.cli import CLIPlots

cp = CLIPlots()

import numpy as np

def load_regression_results(path):
    df = pds.read_csv(path, sep=';')
    df['predicted'] *= 100
    df['observed']  *= 100

    df['abs_error'] = df.predicted - df.observed
    df['abs_error'] = df.abs_error.abs()
    df['squared_error'] = df.abs_error * df.abs_error

    df['baseline'] = df.features.apply(lambda x: correct(x.split(' ')[0]))
    df['baseline'] = df.baseline.apply(lambda x: f'${x}$')
    def case(x):
        xs = x.split(' ')
        cases = ['Quantitative','Quantitative + Qualitative', 'Quantitative + Qualitative + tau']
        return cases[len(xs) - 1]

    cond = np.isin(df.features, ['b', 'b Q', 'b Q tau'
                                ,'B', 'B Q', 'B Q tau'
                                ,'L1', 'L1 Q', 'L1 Q tau'])

    df['cases'] = df.features.apply(lambda x: case(x))

    return df[cond]

TITLE_ERRATA = {
    'tau': '\\tau',
    'B': 'BW^{L2 + DRAM}',
    'b': 'BW^{DRAM}',
    'L1': 'BW^{L2}'
}

def correct(x):
    if x in TITLE_ERRATA.keys():
        return TITLE_ERRATA[x]
    return x

def title_string(features):
    tokens = features.split(' ')
    tokens = [correct(token) for token in tokens]

    return ' '.join([f'${token}$' for token in tokens])

@cp.cli_plot('default')
def plot_regression_results(cli_args):
    sns.set_style('whitegrid')
    df = load_regression_results('../data/these.reg.csv')
    features = cli_args.features
    df = df[df.features == features]
    training   = df[df.training]
    validation = df[~df.training]
    plt.scatter(training.observed, training.predicted, c='lightgray', alpha=1)
    plt.scatter(validation.observed, validation.predicted, c='red', alpha=0)
    plt.plot(training.observed, training.observed, alpha=1)
    plt.xlabel('Predicted overhead (%)', fontsize=16)
    plt.ylabel('Observed overhead (%)', fontsize=16)

    plt.title(title_string(features), fontsize=24)

    mae = validation.abs_error.mean()
    mse = validation.squared_error.mean()

    plt.text(300, -200, f'$MSE={mse:.2f}$        $MAE={mae:.2f}$', fontsize=24, horizontalalignment='center')

@cp.cli_plot('qualitative-gain')
def gain_plot(cli_args):
    df = load_regression_results('../data/these.reg.csv')

    df = df[~df.training].groupby(['features', 'baseline', 'cases']).squared_error.mean().apply(np.sqrt).reset_index()
    print(df)
    hue_order = ['$BW^{L2}$', '$BW^{DRAM}$','$BW^{L2 + DRAM}$']
    width = 0.1

    # sns.lineplot(data=df, x='cases', y='squared_error', hue='baseline', hue_order=hue_order)
    sns.barplot(data=df, x='cases', y='squared_error', hue='baseline', hue_order=hue_order)
    #plt.yscale('log')

if __name__ == '__main__':
    cp._arg_parser.add_argument('--features')

    cp.run()
