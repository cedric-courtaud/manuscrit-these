import pandas as pds
import seaborn as sns
import matplotlib.pyplot as plt

def xp_set_rows(df, s):
    return df.xp_set == s

def prepare_df(df):
	df['compute'] = df.benchmark.apply(lambda x : int(x.split('-')[-1]))

	deps_rows = xp_set_rows(df, 'deps')
	
	df.loc[deps_rows, 'write'] = 1
	df.loc[deps_rows, 'read'] = 1

	df.loc[~deps_rows, 'write'] = df[~deps_rows].benchmark.apply(lambda x : int(x.split('-')[-2]))
	df.loc[~deps_rows, 'read'] = df[~deps_rows].benchmark.apply(lambda x : int(x.split('-')[-3]))

	stream_rows = xp_set_rows(df, 'stream')
	membench_rows = xp_set_rows(df, 'membench')
	sm_rows = stream_rows | membench_rows

	df['template'] = 'rcw'

	df.loc[stream_rows, 'template'] = df[stream_rows].benchmark.apply(lambda x : x.split('-')[1])
	df.loc[membench_rows, 'template'] = df[membench_rows].benchmark.apply(lambda x: x.split('-')[-5])
	df['instance'] = df.benchmark.apply(lambda x: '-'.join(x.split('-')[:-1]))
	
	df['throttle'] = df['compute']
	df.loc[sm_rows, 'compute'] = (df[sm_rows].read + df[sm_rows].write) * df[sm_rows].throttle
	df.loc[~sm_rows, 'throttle'] = df[~sm_rows].compute / (df[~sm_rows].read + df[~sm_rows].write) 

	df['size_KiB'] = 1024

	df.loc[sm_rows, 'size_KiB'] = df[sm_rows].benchmark.apply(lambda x: int(x.split('-')[-4]))

	df['exceed_cache'] = df.size_KiB > 256

	return df

import numpy as np
def plot(df, template):
	df = df.sort_values(by=['compute'])
	df[(df.template == template) & df.exceed_cache]
	df['log_throttle'] = np.log10(1+df.throttle)
	ax = sns.lineplot(data=df, x='log_throttle', y='overhead', hue='instance', linewidth=1, alpha=.5)
	ax.get_legend().remove()

	plt.show()

if __name__ == '__main__':
	df = pds.read_csv('data/training.raw.csv', sep=';')
	df = df[df.overhead == df.max_overhead]
	df = prepare_df(df)

	plot(df, 'rcw')