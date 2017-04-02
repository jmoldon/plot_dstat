import pandas as pd
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.io import vplot
from bokeh.driving import linear
from bokeh.models import Range1d
import os
import subprocess
import time
from bokeh.layouts import gridplot

csv_file = 'test.csv'
time_step = 1 # seconds
f_int = 20
w1, h1 = 300, 150
w2, h2 = 800, 150

mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)

p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(csv_file, time_step)], shell=True, stdout=open(os.devnull, 'w'))


def add_line(p, c, lw, a, legend = ''):
    r = p.line([], [], color=c, line_width=lw, alpha = a, legend = legend)
    ds = r.data_source
    return r, ds

def generate_plot(w, h, follow=False, follow_interval=0):
    p = figure(plot_width=w, plot_height=h)
    if follow:
        p.x_range.follow = "end"
        p.x_range.follow_interval = 20
        p.x_range.range_padding = 0
    return p


p0a = generate_plot(w1, h1, follow=True, follow_interval=f_int)
p1a = generate_plot(w1, h1, follow=True, follow_interval=f_int)
p2a = generate_plot(w1, h1, follow=True, follow_interval=f_int)
p3a = generate_plot(w1, h1, follow=True, follow_interval=f_int)
p4a = generate_plot(w1, h1, follow=True, follow_interval=f_int)

p0b = generate_plot(w2, h2)
p1b = generate_plot(w2, h2)
p2b = generate_plot(w2, h2)
p3b = generate_plot(w2, h2)
p4b = generate_plot(w2, h2)

r0a_0, ds0a_0 = add_line(p0a, lw=3, a=0.4, c="green", legend = 'Mem')
r0a_1, ds0a_1 = add_line(p0a, lw=3, a=0.4, c="red", legend = 'Swap')
r1a_0, ds1a_0 = add_line(p1a, lw=3, a=0.4, c="firebrick", legend = 'CPU')
r2a_0, ds2a_0 = add_line(p2a, lw=3, a=0.4, c="green", legend = 'Read')
r2a_1, ds2a_1 = add_line(p2a, lw=3, a=0.4, c="blue", legend = "Write")
r3a_0, ds3a_0 = add_line(p3a, lw=1, a=1.0, c="black", legend = 'Load')
r3a_1, ds3a_1 = add_line(p3a, lw=5, a=0.3, c="black")
r3a_2, ds3a_2 = add_line(p3a, lw=15, a=0.1, c="black")

r0b_0, ds0b_0 = add_line(p0b, lw=3, a=0.4, c="green", legend = 'Mem')
r0b_1, ds0b_1 = add_line(p0b, lw=3, a=0.4, c="red", legend = 'Swap')
r1b_0, ds1b_0 = add_line(p1b, lw=3, a=0.4, c="firebrick", legend = 'CPU')
r2b_0, ds2b_0 = add_line(p2b, lw=3, a=0.4, c="green",  legend = 'Read')
r2b_1, ds2b_1 = add_line(p2b, lw=3, a=0.4, c="blue", legend = 'Write')
r3b_0, ds3b_0 = add_line(p3b, lw=1, a=1.0, c="black", legend = 'Load')
r3b_1, ds3b_1 = add_line(p3b, lw=5, a=0.3, c="black")
r3b_2, ds3b_2 = add_line(p3b, lw=15, a=0.1, c="black")


p0a.y_range.start = 0.0
p0a.y_range.end = mem_gib
p1a.y_range.start = 0.
p1a.y_range.end = 100.

p0b.y_range.start = 0.0
p0b.y_range.end = mem_gib
p1b.y_range.start = 0.
p1b.y_range.end = 100.

p= gridplot([[p0a, p0b],
[p1a, p1b],
[p2a, p2b],
[p3a, p3b]])

def add_resource(ds, step, value):
    ds.data['x'].append(step)
    ds.data['y'].append(value)
    ds.trigger('data', ds.data, ds.data)
    return ds


@linear()
def update(step):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    add_resource(ds0a_0, step, float(df['used'].iloc[-1])/(1024*1024*1024))
    add_resource(ds0a_1, step, float(df['used.1'].iloc[-1])/(1024*1024*1024))
    add_resource(ds1a_0, step, (100.-float(df['idl'].iloc[-1])))
    add_resource(ds2a_0, step, float(df['read'].iloc[-1])/(1024*1024))
    add_resource(ds2a_1, step, float(df['writ'].iloc[-1])/(1024*1024))
    add_resource(ds3a_0, step, float(df['1m'].iloc[-1]))
    add_resource(ds3a_1, step, float(df['5m'].iloc[-1]))
    add_resource(ds3a_2, step, float(df['15m'].iloc[-1]))

    add_resource(ds0b_0, step, float(df['used'].iloc[-1])/(1024*1024*1024))
    add_resource(ds0b_1, step, float(df['used.1'].iloc[-1])/(1024*1024*1024))
    add_resource(ds1b_0, step, (100.-float(df['idl'].iloc[-1])))
    add_resource(ds2b_0, step, float(df['read'].iloc[-1])/(1024*1024))
    add_resource(ds2b_1, step, float(df['writ'].iloc[-1])/(1024*1024))
    add_resource(ds3b_0, step, float(df['1m'].iloc[-1]))
    add_resource(ds3b_1, step, float(df['5m'].iloc[-1]))
    add_resource(ds3b_2, step, float(df['15m'].iloc[-1]))


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 1000)



#kk = raw_input('Working')

print 'Go terminate'
p_dstat.terminate()
print 'End program'

