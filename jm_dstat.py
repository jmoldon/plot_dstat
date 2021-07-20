#! /mirror1/scratch/jmoldon/software/conda/envs/jmpy/bin/python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.dates import date2num, AutoDateFormatter, AutoDateLocator
import matplotlib.dates as mdates
import datetime
import subprocess
import os, sys
import time
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



def c(i):
    NUM_COLORS = 10
    i = i%10
    cm = plt.get_cmap('prism')
    cNorm  = matplotlib.colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
    scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=cm)
    return scalarMap.to_rgba(i)


def start_dstat(outfile, time_step):
    p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(outfile, time_step)], shell=True, stdout=open(os.devnull, 'w'))
    print('dstat running on the background')
    return p_dstat

def end_dstat(p):
    p.terminate()
    print('End dstat')


def read_csv(csv_file, resample=1):
    input_a = np.genfromtxt(csv_file, delimiter=',', skip_header=5, names=True,dtype=None)
    names = input_a.dtype.names
    a = {}
    if resample == 'auto':
        resample = int(len(input_a['epoch'])/800.)
        resample = np.min([np.max([resample, 1]), 120])  # resample within [1s, 2min]
        print('Resampling by {}s'.format(resample))
    else:
        print('Resampling by {}s'.format(resample))
    for k in names:
        a[k] = np_resample(input_a[k], resample)

    data = {}
    data['date'] = np.array([datetime.datetime(*time.gmtime(t)[:6]) for t in a['epoch']])
    data['read'] = np.array([a[n] for n in names if 'read' in n]).sum(axis=0)
    data['writ'] = np.array([a[n] for n in names if 'writ' in n]).sum(axis=0)
    data['used'] = a['used']
    data['used_1'] = a['used_1']
    data['idl'] = a['idl']
    data['l_1m'] = a['1m']
    data['l_5m'] = a['5m']
    data['l_15m'] = a['15m']
    return data


def np_resample(a, factor=2):
    return np.interp(np.arange(0, len(a), factor), np.arange(0, len(a)), a)

def plot_dstat(data, start_time, input_command, summary, do_sum=False):
    mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)
    lw1 = 1.5
    a1 = 1.0
    fig, ax = plt.subplots(4, sharex =True, figsize = (10, 8))
    plt.subplots_adjust(hspace = .1)
    ax[0].plot(data['date'], data['used']/(1024*1024*1024), color='blue', label='Mem', lw=lw1, alpha=a1)
    ax[0].plot(data['date'], data['used_1']/(1024*1024*1024), color='red', label='Swap', lw=lw1, alpha=a1)
    ax[1].plot(data['date'], 100.-data['idl'], color='k', label='CPU', lw=lw1, alpha=a1)
    ax[2].plot(data['date'], data['read']/(1024*1024), color='green', label='Read', lw=lw1, alpha=a1)
    ax[2].plot(data['date'], data['writ']/(1024*1024), color='magenta', label='Write', lw=lw1, alpha=a1)
    ax[3].plot(data['date'], data['l_1m'], color='black', label='Load', lw=1, alpha=1.0)
    ax[3].plot(data['date'], data['l_5m'], color='black', lw=5, alpha=0.3)
    ax[3].plot(data['date'], data['l_15m'], color='black', lw=10, alpha=0.1)

#    ax[0].set_ylim(0.0, mem_gib)
    ax[1].set_ylim(0.0, 100)
    ax[3].set_ylim(0, ax[3].get_ylim()[-1])

    ax[0].set_ylabel('Memory [GB]')
    ax[1].set_ylabel('CPU %')
    ax[2].set_ylabel('Disk I/O [MB/s]')
    ax[3].set_ylabel('Load')
    ax[-1].set_xlabel('Time UTC')
    total_time = data['date'][-1] - data['date'][0]
    ax[0].set_title('shell command: {0}\nStart time: {1} | Total time: {2}'.format(input_command,
                                                start_time.strftime(format='%Y-%m-%d %H:%M:%S'),
                                                total_time))
    for axi in ax:
        axi.legend(loc = 0, ncol = 1, fontsize = 'small')



    xlim = ax[3].get_xlim()

    xtick_locator = AutoDateLocator()
    #xtick_formatter = AutoDateFormatter(xtick_locator)
    myFmt = mdates.DateFormatter('%H:%M:%S')

    for axi in ax:
        axi.xaxis.set_major_locator(xtick_locator)
        axi.xaxis.set_major_formatter(myFmt)

    fig.autofmt_xdate()
    outfile = 'usage_{}.png'.format(start_time.strftime(format='%Y%m%d_%H%M%S'))
    fig.savefig(outfile, bbox_inches='tight')

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
    if '.csv' in sys.argv[-1]:
        csv_file = sys.argv[-1]
        input_command = ''
        datetime_filename = csv_file.split('dstat_')[-1][:-4]
        start_time = datetime.datetime.strptime(datetime_filename, '%Y%m%d_%H%M%S')
    else:
        start_time = datetime.datetime.now()
        print(start_time)
        csv_file = 'dstat_{}.csv'.format(start_time.strftime(format='%Y%m%d_%H%M%S'))
        input_command = sys.argv[-1]
        p = start_dstat(csv_file, time_step=1)
        print('Running command: {}'.format(input_command))
        os.system(input_command)
        end_dstat(p)
    # Produce plot from csv
    #data = read_csv(csv_file)
    data = read_csv(csv_file, resample=4)
    summary = 'eMCP.log'
    plot_dstat(data, start_time, input_command, summary, do_sum=True)

