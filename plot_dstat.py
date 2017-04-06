import pandas as pd
import numpy as np
import subprocess
import os, sys
import time

from bokeh.plotting import figure, show, output_file, vplot, save
#from bokeh.embed import file_html
from bokeh.io import gridplot, output_file, show

import bokeh
print bokeh.__version__

output_file("usage.html", title="Usage")

csv_file = 'test.csv'
time_step = 1 # seconds

w1, h1 = 300, 150
w2, h2 = 800, 150
TOOLS = ['pan','box_zoom','resize', 'save', 'reset']

def start_dstat(outfile, time_step):
    os.system('mv {0} {1}'.format(outfile, outfile+'_old'))
    p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(outfile, time_step)], shell=True, stdout=open(os.devnull, 'w'))
    print('dstat running on the background')
    return p_dstat

def end_dstat(p):
    p.terminate()
    print 'End dstat'


def plot_dstat(csv_file):
    df = read_csv(csv_file)
    mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)
    p0 = figure(plot_width=w2, plot_height=h2, x_axis_type = "datetime", tools = TOOLS)
    p1 = figure(plot_width=w2, plot_height=h2, x_axis_type = "datetime", tools = TOOLS)
    p2 = figure(plot_width=w2, plot_height=h2, x_axis_type = "datetime", tools = TOOLS)
    p3 = figure(plot_width=w2, plot_height=h2, x_axis_type = "datetime", tools = TOOLS)
    p4 = figure(plot_width=w2, plot_height=h2, x_axis_type = "datetime", tools = TOOLS)

    p0.line(df['date'], df['used']/(1024*1024*1024), color='blue', legend='Mem', line_width=3, alpha=0.4)
    p0.line(df['date'], df['used.1']/(1024*1024*1024), color='red', legend='Swap', line_width=3, alpha=0.4)
    p1.line(df['date'], 100.-df['idl'], color='firebrick', legend='CPU', line_width=3, alpha=0.4)
    p2.line(df['date'], df['read']/(1024*1024), color='green', legend='Read', line_width=3, alpha=0.4)
    p2.line(df['date'], df['writ']/(1024*1024), color='blue', legend='Write', line_width=3, alpha=0.4)
    p3.line(df['date'], df['1m'], color='black', legend='Load', line_width=1, alpha=1.0)
    p3.line(df['date'], df['5m'], color='black', line_width=5, alpha=0.3)
    p3.line(df['date'], df['15m'], color='black', line_width=15, alpha=0.1)

    p0.y_range.start = 0.0
    p0.y_range.end = mem_gib
    p1.y_range.start = 0.
    p1.y_range.end = 100.
    p3.y_range.start = 0.

    ps = [p0,p1,p2,p3]
    for pi in ps:
        try:
            pi.legend.location = "top_left"
            pi.legend.padding = 5
        except:
            pi.legend.orientation = 'top_left'

    p= gridplot([[p0],
    [p1],
    [p2],
    [p3]])

    save(p, 'plots/usage.html')

def read_csv(csv_file):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    df = df[df.epoch > 1e9]
    df['date'] = pd.to_datetime(df['epoch'],unit='s')

    return df

if __name__ == '__main__':
    p = start_dstat(csv_file, time_step)
    time.sleep(60*60*1)
    end_dstat(p)
    plot_dstat(csv_file)

