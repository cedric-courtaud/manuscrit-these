import pandas as pds
import seaborn as sns
import matplotlib.pyplot as plt
from pthese.cli import CLIPlots
import matplotlib as mpl

cp = CLIPlots()

def load_data():
    df1 = pds.read_csv('data/membench_agg.filtered.raw.csv', sep=';')
    df2 = pds.read_csv('data/stream_agg.filtered.raw.csv', sep=';')

    df = pds.concat([df1, df2])

    df['l1_bw_iso'] = (32 * df.Data_cache_miss / 1_000_000) / (df.total_cycles_iso / 1_000_000_000)

    filter_criterion = (df.template == 'rcw') & \
                       (df.size_KiB != 256) & \
                       (~df.discarded) & \
                       (df.overhead == df.max_overhead)

    return df[filter_criterion]


@cp.cli_plot('throttle-overhead-stream')
def plot_throttle_overhead_stream(cli_args):
    def mlp(x):
        xs = x.split('-')
        if xs[0] == '1':
            return xs[1]
        return xs[0]

    def t(x):
        xs = x.split('-')
        if xs[0] == '1':
            return '1-mlp'
        if xs[1] == '1':
            return 'mlp-1'

        return 'mlp-mlp'

    df = load_data()
    d = df[df.xp_set == 'stream']
    d = d[~d.discarded]
    d['mlp'] = d.rw.apply(mlp)
    d = d[d.mlp != 1]
    d['$R-W$'] = d.rw.apply(t)
    g = sns.FacetGrid(data=d, row='mlp', col='stride', hue='$R-W$', row_order=['2', '4', '8', '16'], size=3, aspect=1.5,
                      palette='magma', margin_titles=True, legend_out=True)
    g.map(sns.lineplot, 'throttle', 'overhead')
    g.set(xscale='symlog', xlabel='$F$', ylabel='Overhead (%)')
    g.add_legend()
    # plt.savefig('/home/calimero/these/manuscrit/graphics/figures/throttle_overhead_stream.pdf', bbox_inches='tight')

@cp.cli_plot('throttle-overhead-membench')
def plot_throttle_overhead_membench(cli_args):
    df = load_data()
    d = df[df.xp_set == 'membench']

    def BL(x):
        tkns = [int(i) for i in x.split('-')]
        if (tkns[0] + tkns[1]) > 40:
            return 50
        return 4

    def rw(x):
        print(x)
        tkns = [int(i) for i in x.split('-')]
        return tkns[0] / (tkns[0] + tkns[1])

    #d['rw']=d.benchmark.apply(rw)
    d['ratio'] = d.rw.apply(rw)
    d['BL'] = d.rw.apply(BL)
    d['Comportement'] = d.pattern
    d['$R-W$'] = d.rw
    col_order=['linear','random',
               'scatter','gather',
               'linear-lookup','shuffled-lookup',
               'linear-list', 'shuffled-list']
    hue_order=[  '0-4','0-50','1-3', '12-37','2-2','25-25', '3-1','37-12','4-0','50-0']

    g = sns.FacetGrid(data=d, col='Comportement', hue='$R-W$',
                      col_wrap=2,aspect=1.5,size=3, col_order=col_order,hue_order=hue_order, palette='magma',
                      legend_out=True, margin_titles=True)

    g.map(sns.lineplot, 'throttle', 'overhead').set_titles('{col_name}')
    # g.map(sns.lineplot, 'throttle', 'model')

    g.set(xscale='symlog', xlabel='$F$', ylabel='Overhead (%)')
    g.add_legend()

def annotate_death_zone(ax, alpha=0.25):
    mpl.rcParams['hatch.linewidth'] = 6.0  # previous svg hatch linewidth
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    ax.text(x_max, 300 + (y_max - 300) / 2, '$\\frac{T_{cont}}{T_{iso}} > N_{core}$',
            horizontalalignment='left', verticalalignment='center', rotation=90, zorder=3)
    ax.axhspan(300, ax.get_ylim()[1],0, 0.97, color='r', fill=False, alpha=alpha, hatch='//', lw=0, zorder=1)


@cp.cli_plot('throttle-overhead-all')
def throttle_overhead_all_log(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    size=4
    if cli_args.big:
        size = 7
    g = sns.FacetGrid(data=df.sort_values(by=['throttle']), hue='instance', palette=palette, sharey=True, size=size,
                      aspect=1.3)

    g.map(sns.lineplot, 'throttle', 'overhead', alpha=0.35, linewidth=0.5, zorder=3)

    bar_color = 'teal'

    ax = g.axes[0][0]
    ax.axvline(0, 0.28, 0.95, ls='--', c=bar_color, zorder=5)
    ax.axvline(10, 0.11, 0.72, ls='--', c=bar_color, zorder=5)

    ax.axvline(100, 0.07, 0.26, ls='--', c=bar_color, zorder=5)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=bar_color, zorder=5)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=bar_color, zorder=5)
    d1 = df[df.instance == 'linear-rcw-16384-0-4']
    d2 = df[df.instance == 'linear-rcw-16384-50-0']

    ax.plot(d1.throttle, d1.overhead, zorder=4)
    ax.plot(d2.throttle, d2.overhead, zorder=4)

    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()

    annotate_death_zone(ax, alpha=0.1)
    xmax += 0.05 * xmax
    g.set(xlabel='$F$', ylabel='Overhead(%)', ylim=(ymin, ymax), xlim=(xmin, xmax))

    # # ax.text(10500, 290, '$Overhead = N_{CORE} - 1$', horizontalalignment='right')
    # ax.axhspan(300, ax.get_ylim()[1], color='r',fill=False, alpha=0.1, hatch='\\', lw=0, edgecolor='red')
    # print(xlim)

@cp.cli_plot('throttle-overhead-log-colors')
def throttle_overhead_all_log(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    # palette = 'magma'
    size=4

    if cli_args.big:
        size = 7

    g = sns.FacetGrid(data=df.sort_values(by=['throttle']), hue='instance', palette=palette, sharey=True, size=size,
                      aspect=1.3)

    g.map(sns.lineplot, 'throttle', 'overhead', alpha=0.35, linewidth=0.5, zorder=3)

    bar_color = 'teal'

    ax = g.axes[0][0]
    # ax.axhline(300, 0, 0.67, ls='-', c='red', linewidth=1)

    ax.axvline(0, 0.28, 0.95, ls='--', c=bar_color)
    ax.axvline(10, 0.11, 0.72, ls='--', c=bar_color)
    #
    ax.axvline(100, 0.07, 0.26, ls='--', c=bar_color)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=bar_color)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=bar_color)

    #d1 = df[df.instance == 'linear-rcw-16384-0-4']
    # d2 = df[df.instance == 'linear-rcw-16384-50-0']
    #
    # ax.plot(d1.throttle, d1.overhead)
    # ax.plot(d2.throttle, d2.overhead)

    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()

    annotate_death_zone(ax, alpha=0.1)
    xmax += 0.25 * xmax
    g.set(xscale='symlog', xlabel='$T$', ylabel='Overhead(%)', ylim=(ymin, ymax), xlim=(-0.1,xmax))

    # # ax.text(10500, 290, '$Overhead = N_{CORE} - 1$', horizontalalignment='right')
    # ax.axhspan(300, ax.get_ylim()[1], color='r',fill=False, alpha=0.1, hatch='\\', lw=0, edgecolor='red')
    # print(xlim)

@cp.cli_plot('throttle-overhead-log-all')
def throttle_overhead_all_log(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    size=4

    if cli_args.big:
        size = 7

    g = sns.FacetGrid(data=df.sort_values(by=['throttle']), hue='instance', palette=palette, sharey=True, size=size,
                      aspect=1.3)

    g.map(sns.lineplot, 'throttle', 'overhead', alpha=0.35, linewidth=0.5, zorder=3)

    bar_color = 'teal'

    ax = g.axes[0][0]
    # ax.axhline(300, 0, 0.67, ls='-', c='red', linewidth=1)

    # ax.axvline(0, 0.28, 0.95, ls='--', c=bar_color)
    ax.axvline(10, 0.11, 0.72, ls='--', c=bar_color)

    # ax.axvline(100, 0.07, 0.26, ls='--', c=bar_color)
    # ax.axvline(1_000, 0.05, 0.09, ls='--', c=bar_color)
    # ax.axvline(10_000, 0.05, 0.055, ls='--', c=bar_color)
    d1 = df[df.instance == 'linear-rcw-16384-0-4']
    d2 = df[df.instance == 'linear-rcw-16384-50-0']

    ax.plot(d1.throttle, d1.overhead)
    ax.plot(d2.throttle, d2.overhead)

    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()

    annotate_death_zone(ax, alpha=0.1)
    xmax += 0.25 * xmax
    g.set(xscale='symlog', xlabel='$F$', ylabel='Overhead(%)', ylim=(ymin, ymax), xlim=(-0.1,xmax))

    # # ax.text(10500, 290, '$Overhead = N_{CORE} - 1$', horizontalalignment='right')
    # ax.axhspan(300, ax.get_ylim()[1], color='r',fill=False, alpha=0.1, hatch='\\', lw=0, edgecolor='red')
    # print(xlim)


@cp.cli_plot('distribution-l1bw-bw')
def throttle_overhead_all_log(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    size=4

    if cli_args.big:
        size = 7

    sns.set_style('whitegrid')
    h = sns.jointplot(data=df, x='bw_iso', y='l1_bw_iso')
    h.set_axis_labels('$BW_{iso}^{DRAM}$(MiB/s)','$BW_{iso}^{L2}$(MiB/s)')
    h.ax_joint.plot(df.bw_iso, df.bw_iso, '--', c='g')
    h.ax_joint.plot(df.bw_iso, df.bw_iso / 2, '--', c='r')

    # sns.scatterplot(df.bw_iso, df.l1_bw_iso)
    # sns.lineplot(df.bw_iso, df.bw_iso, linewidth=1, color='r')

    # plt.xlabel('$BW_{iso}^{DRAM}$(MiB/s)')
    # plt.ylabel('$BW_{iso}^{L2}$(MiB/s)')


@cp.cli_plot('throttle-bw-all')
def throttle_bw_all_lpog(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    size=4
    if cli_args.big:
        size = 7
    g = sns.FacetGrid(data=df.sort_values(by=['throttle']), hue='instance', palette=palette, sharey=True, size=size,
                      aspect=1.6)

    g.map(sns.lineplot, 'throttle', 'bw_iso', alpha=0.8, linewidth=0.5)

    C1 = 'teal'
    ax = g.axes[0][0]
    '''
    ax.axhline(300, 0.025, 0.99, ls=':', c='red')
    ax.axvline(0, 0.28, 0.95, ls='--', c=C1)
    ax.axvline(10, 0.11, 0.72, ls='--', c=C1)

    ax.axvline(100, 0.07, 0.26, ls='--', c=C1)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=C1)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=C1)
    ax.text(11_000, 310, '$Overhead > N_{CORE}$', horizontalalignment='right')
    '''

    d1 = df[df.instance == 'linear-rcw-16384-0-4']
    d2 = df[df.instance == 'linear-rcw-16384-50-0']

    #ax.plot(d1.throttle, d1.overhead)
    #ax.plot(d2.throttle, d2.overhead)

    g.set(xscale='symlog', xlabel='$F$', ylabel='$BW_{iso}^{DRAM}$(MiB/s)')

@cp.cli_plot('throttle-l1bw-all')
def throttle_bw_all_log(cli_args):
    df = load_data()
    palette = sns.color_palette(len(df.instance.unique()) * ['gray'])
    size=4
    if cli_args.big:
        size = 7
    g = sns.FacetGrid(data=df.sort_values(by=['throttle']), hue='instance', palette=palette, sharey=True, size=size,
                      aspect=1.6)

    g.map(sns.lineplot, 'throttle', 'l1_bw_iso', alpha=0.8, linewidth=0.5)


    C1 = 'teal'
    ax = g.axes[0][0]
    '''
    ax.axhline(300, 0.025, 0.99, ls=':', c='red')
    ax.axvline(0, 0.28, 0.95, ls='--', c=C1)
    ax.axvline(10, 0.11, 0.72, ls='--', c=C1)

    ax.axvline(100, 0.07, 0.26, ls='--', c=C1)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=C1)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=C1)
    ax.text(11_000, 310, '$Overhead > N_{CORE}$', horizontalalignment='right')
    '''

    d1 = df[df.instance == 'linear-rcw-16384-0-4']
    d2 = df[df.instance == 'linear-rcw-16384-50-0']

    #ax.plot(d1.throttle, d1.overhead)
    #ax.plot(d2.throttle, d2.overhead)

    g.set(xscale='symlog', xlabel='$F$', ylabel='$BW_{iso}^{L2}$(MiB/s)')



def do_plot_bw_overhead_annot(df, bw_col, is_big=True, xlabel=None):
    palette = sns.color_palette(len(df.instance.unique()) * ['lightgray'])

    size = 4
    if is_big:
        size = 7

    g = sns.FacetGrid(data=df.sort_values(by=[bw_col]),
                      palette=palette,
                      sharey=True,
                      size=size,
                      aspect=1.6)

    g.map(plt.scatter, bw_col, 'overhead', alpha=0.7, zorder=3, linewidth=None, s=4)

    ax = g.axes[0][0]
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    min_300 = df[df.overhead > 300]
    min_300 = min_300[min_300[bw_col] == min_300[bw_col].min()].iloc[0]

    # ax.axhline(300, 0.025, 0.99, ls=':', c='red')
    ax.axvline(min_300[bw_col], 0.05, 0.95, ls=':', c='red', zorder=5)
    ax.scatter(min_300[bw_col], min_300.overhead, s=7, c='r', zorder=6)
    annotate_death_zone(ax)
    #ax.text(x_max, 300 + (y_max - 300) / 2, '$\\frac{T_{cont}}{T_{iso}} > N_{core}$', horizontalalignment='left', rotation=90, zorder=3)
    x_max += 0.025 * x_max

    g.set(xlabel=xlabel, ylabel='Overhead(%)', xlim=(x_min, x_max))



    '''

    ax.text(2000, 310, '$Overhead > N_{CORE}$', horizontalalignment='right')

    '''


@cp.cli_plot('bw-overhead-annot')
def bw_overhead_annot(cli_args):
    df = load_data()
    do_plot_bw_overhead_annot(df, 'bw_iso', is_big=cli_args.big, xlabel='$BW_{iso}^{DRAM}$(MiB/s)')
    # palette = sns.color_palette(len(df.instance.unique()) * ['lightgray'])


    # size = 4
    #
    # if cli_args.big:
    #     size = 7
    # g = sns.FacetGrid(data=df.sort_values(by=['bw_iso']), palette=palette, sharey=True, size=size,
    #                   aspect=1.6)
    #
    # g.map(sns.scatterplot, 'bw_iso', 'overhead', alpha=0.8, linewidth=0.5)
    # ax = g.axes[0][0]
    # ax.axhline(300, 0.025, 0.99, ls=':', c='red')
    # ax.axvline(200, 0.05, 0.95, ls=':', c='red')
    #
    # g.set(xlabel='$BW_{iso}^{DRAM}$(MiB/s)', ylabel='Overhead(%)')
    #
    #
    # mpl.rcParams['hatch.linewidth'] = 5.0  # previous svg hatch linewidth
    # # ax.text(10500, 290, '$Overhead = N_{CORE} - 1$', horizontalalignment='right')
    # ax.axhspan(300, ax.get_ylim()[1], color='r',fill=False, alpha=0.1, hatch='\\', lw=1, edgecolor='red')

    '''
    C1 = 'teal'

    ax.axvline(0, 0.28, 0.95, ls='--', c=C1)
    ax.axvline(10, 0.11, 0.72, ls='--', c=C1)

    ax.axvline(100, 0.07, 0.26, ls='--', c=C1)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=C1)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=C1)

    ax.text(2000, 310, '$Overhead > N_{CORE}$', horizontalalignment='right')
    
    '''


@cp.cli_plot('bw-overhead-annot')
def bw_overhead_annot(cli_args):
    df = load_data()
    do_plot_bw_overhead_annot(df, 'bw_iso', is_big=cli_args.big, xlabel='$BW_{iso}^{DRAM}$(MiB/s)')
    # palette = sns.color_palette(len(df.instance.unique()) * ['lightgray'])

    # size = 4
    #
    # if cli_args.big:
    #     size = 7
    # g = sns.FacetGrid(data=df.sort_values(by=['bw_iso']), palette=palette, sharey=True, size=size,
    #                   aspect=1.6)
    #
    # g.map(sns.scatterplot, 'bw_iso', 'overhead', alpha=0.8, linewidth=0.5)
    # ax = g.axes[0][0]
    # ax.axhline(300, 0.025, 0.99, ls=':', c='red')
    # ax.axvline(200, 0.05, 0.95, ls=':', c='red')
    #
    # g.set(xlabel='$BW_{iso}^{DRAM}$(MiB/s)', ylabel='Overhead(%)')
    #
    #
    # mpl.rcParams['hatch.linewidth'] = 5.0  # previous svg hatch linewidth
    # # ax.text(10500, 290, '$Overhead = N_{CORE} - 1$', horizontalalignment='right')
    # ax.axhspan(300, ax.get_ylim()[1], color='r',fill=False, alpha=0.1, hatch='\\', lw=1, edgecolor='red')

    '''
    C1 = 'teal'

    ax.axvline(0, 0.28, 0.95, ls='--', c=C1)
    ax.axvline(10, 0.11, 0.72, ls='--', c=C1)

    ax.axvline(100, 0.07, 0.26, ls='--', c=C1)
    ax.axvline(1_000, 0.05, 0.09, ls='--', c=C1)
    ax.axvline(10_000, 0.05, 0.055, ls='--', c=C1)

    ax.text(2000, 310, '$Overhead > N_{CORE}$', horizontalalignment='right')

    '''


@cp.cli_plot('l1bw-overhead-annot')
def bw_overhead_annot(cli_args):
    df = load_data()
    do_plot_bw_overhead_annot(df, 'l1_bw_iso', is_big=cli_args.big, xlabel='$BW_{iso}^{L2}$(MiB/s)')


@cp.cli_plot('conservative-inference')
def plot_conservative_inferences(cli_args):
    df = load_data().sort_values(by='bw_iso')

    sns.set_style('whitegrid')

    sns.scatterplot(data=df, x='bw_iso', y='overhead')
    sns.lineplot(df.bw_iso, df.overhead.cummax(),c='r')
    plt.xlabel('$BW_{iso}^{DRAM}$(MiB/s)')
    plt.ylabel('Overhead(%)')

if __name__ == '__main__':
    cp._arg_parser.add_argument('--annotate', action='store_true')
    cp._arg_parser.add_argument('--big', action='store_true')
    cp.run()
