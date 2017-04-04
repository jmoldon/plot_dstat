import pandas as pd
import numpy as np
import subprocess
import os, sys
import time

csv_file = 'test.csv'
time_step = 1 # seconds

def start_dstat(outfile, time_step):
    p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(outfile, time_step)], shell=True, stdout=open(os.devnull, 'w'))
    print('dstat running on the background')
    return p_dstat

def end_dstat(p):
    p.terminate()
    print 'End dstat'


def plot_dstat():
    mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)

def read_csv(csv_file):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    return df

if __name__ == '__main__':
    p = start_dstat(csv_file, time_step)
    time.sleep(100)
    end_dstat(p)
    df = read_csv(csv_file)


