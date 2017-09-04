import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import subprocess
import os, sys
import time

csv_file = 'test.csv'
logfile = 'eMCP.log'

time_step = 1 # seconds

def c(i):
    NUM_COLORS = 10
    i = i%10
    cm = plt.get_cmap('prism')
    cNorm  = matplotlib.colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
    scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=cm)
    return scalarMap.to_rgba(i)

def start_dstat(outfile, time_step):
    os.system('mv {0} {1}'.format(outfile, outfile+'_old'))
    p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(outfile, time_step)], shell=True, stdout=open(os.devnull, 'w'))
    print('dstat running on the background')
    return p_dstat

def end_dstat(p):
    p.terminate()
    print 'End dstat'

def summary_log(logfile):
    df = pd.read_csv(logfile, sep = '|', names = ['date','grade','text'])
    df['date'] = df['date'].apply(lambda x:pd.to_datetime(x)-pd.to_timedelta('1h'))
    df['stat'] = df['text'].apply(lambda x: x.split(' ')[1])
    df['task'] = df['text'].apply(lambda x: x.split(' ')[-1])
    beg = df[['date', 'task']][df['stat'] == 'Start']
    end = df[['date', 'task']][df['stat'] == 'End']
    beg = beg.reset_index(drop=True)
    end = end.reset_index(drop=True)
    summary = pd.merge(beg,end, left_index=True,right_index=True, suffixes = ['_beg', '_end'])
    summary = summary.rename(columns={'task_beg':'task'})[['task','date_beg','date_end']]
    summary['total'] = summary.apply(lambda row: row['date_end'] - row['date_beg'], axis=1)
    summary['total_s'] = summary.apply(lambda x:x['total']/np.timedelta64(1, 's'), axis=1)
    return summary

def read_csv(csv_file):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    df = df[df.epoch > 1e9]
    df['date'] = pd.to_datetime(df['epoch'],unit='s')
    df['read_tot'] = df.filter(regex='read*').sum(axis = 1)
    df['writ_tot'] = df.filter(regex='writ*').sum(axis = 1)
    df.index = df['date']
    return df

def read_log(csv_file, resample = None):
    df = read_csv(csv_file)
    if resample:
        df = df.resample(resample).mean() # For example '5S'
        df['date'] = df.index
    return df

def plot_dstat(df, summary):
    mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)
    lw1 = 1.0
    a1 = 1.0
    fig, ax = plt.subplots(4, sharex =True, figsize = (10, 8))
    plt.subplots_adjust(hspace = .1)
    ax[0].plot(df['date'], df['used']/(1024*1024*1024), color='blue', label='Mem', lw=lw1, alpha=a1)
    ax[0].plot(df['date'], df['used.1']/(1024*1024*1024), color='red', label='Swap', lw=lw1, alpha=a1)
    ax[1].plot(df['date'], 100.-df['idl'], color='k', label='CPU', lw=lw1, alpha=a1)
    ax[2].plot(df['date'], df['read_tot']/(1024*1024), color='green', label='Read', lw=lw1, alpha=a1)
    ax[2].plot(df['date'], df['writ_tot']/(1024*1024), color='blue', label='Write', lw=lw1, alpha=a1)
    ax[3].plot(df['date'], df['1m'], color='black', label='Load', lw=1, alpha=1.0)
    ax[3].plot(df['date'], df['5m'], color='black', lw=5, alpha=0.3)
    ax[3].plot(df['date'], df['15m'], color='black', lw=10, alpha=0.1)

    ax[0].set_ylim(0.0, mem_gib)
    ax[1].set_ylim(0.0, 100)
    ax[3].set_xlim(0, ax[3].get_xlim()[-1])

    for i in range(len(summary)):
        b = summary.iloc[i]['date_beg']
        e = summary.iloc[i]['date_end']
        ax[0].annotate(i, (b, ax[0].get_ylim()[1]*0.9), rotation=0., annotation_clip=False)
        #ax[0].annotate(summary['task'].iloc[i], (b, ax[0].get_ylim()[1]*0.8), rotation=0., annotation_clip=False)
        for axi in ax:
            axi.axvspan(b, e, alpha = 0.2, facecolor = c(i), lw = 0)

    ax[0].set_xlim(summary['date_beg'].min(), summary['date_end'].max())
    ax[0].set_ylabel('Memory [GB]')
    ax[1].set_ylabel('CPU %')
    ax[2].set_ylabel('Disk I/O [MB/s]')
    ax[3].set_ylabel('Load')
    ax[-1].set_xlabel('Time UTC')

    for axi in ax:
        axi.legend(loc = 0, ncol = 1, fontsize = 'small')
    fig.savefig('usage.png', bbox_inches='tight')

def plot_total_time(summary):
    fig = plt.figure(figsize = (8, 12))
    ax = fig.add_subplot(1,1,1)

    for i in range(len(summary)):
        ax.barh(i, summary['total_s'].values[i]/60./60., align='center', facecolor = c(i), alpha = 0.2, lw = 0)
        ax.annotate('   '+prt_total_s(summary['total_s'].values[i]), (0, i), rotation=0., annotation_clip=False)

    ax.yaxis.set_ticks(summary['task'].index)
    yticklabels = ['{1} ({0})'.format(i, ni) for i, ni in enumerate(summary['task'].values)]
    ax.yaxis.set_ticklabels(yticklabels)
    ax.set_xlabel('Total time [h]')
    ax.set_ylim(ax.get_ylim()[-1]-0.5, ax.get_ylim()[0]+0.5)
    ax.set_xlim(0, ax.get_xlim()[-1])
    total_time = (summary['date_end'].max()-summary['date_beg'].min()).total_seconds()
    ax.set_title('Total time [hh:mm:ss]: {0}'.format(prt_total_s(total_time)))
    fig.savefig('summary.png', bbox_inches='tight')

def prt_total_s(s):
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{0:02.0f}:{1:02.0f}:{2:02.0f}'.format(hours, minutes, seconds)



if __name__ == '__main__':
    #p = start_dstat(csv_file, time_step)
    #time.sleep(60*60*1)            # dstat running during specific time
    #stop = raw_input('Stop?')      # dstat running until stopped
    #end_dstat(p)
    print('Reading and processing {0}'.format(logfile))
    summary = summary_log(logfile)
    plot_total_time(summary)
    try:
        df = read_log(csv_file)
        plot_dstat(df, summary)
        print('Processed {0}'.format(csv_file))
    except:
        print('Error. csv_file {0} not found'.format(csv_file))
        pass
