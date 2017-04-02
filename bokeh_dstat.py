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


mem_gib = 1.0*os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')/(1024**3)

p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(csv_file, time_step)], shell=True, stdout=open(os.devnull, 'w'))

height = 150
w1 = 400
w2 = 800
p1 = figure(plot_width=w1, plot_height=height)
r1 = p1.line([], [], color="green", line_width=3, alpha = 0.4)
r1s = p1.line([], [], color="red", line_width=3, alpha = 0.4)
p2 = figure(plot_width=w1, plot_height=height)
r2 = p2.line([], [], color="firebrick", line_width=3, alpha = 0.4)
p3 = figure(plot_width=w1, plot_height=height)
r3 = p3.line([], [], color="green", line_width=3, alpha = 0.4)
p4 = figure(plot_width=w1, plot_height=height)
r4 = p4.line([], [], color="blue", line_width=3, alpha = 0.4)
p5 = figure(plot_width=w1, plot_height=100)
r5_1m  = p5.line([], [], color="black", line_width=1, alpha = 1.0)
r5_5m  = p5.line([], [], color="black", line_width=5, alpha = 0.3)
r5_15m = p5.line([], [], color="black", line_width=15, alpha = 0.1)

p1ct = figure(plot_width=w2, plot_height=height)
r1ct = p1ct.line([], [], color="green", line_width=3, alpha = 0.4)
r1sct = p1ct.line([], [], color="red", line_width=3, alpha = 0.4)
p2ct = figure(plot_width=w2, plot_height=height)
r2ct = p2ct.line([], [], color="firebrick", line_width=3, alpha = 0.4)
p3ct = figure(plot_width=w2, plot_height=height)
r3ct = p3ct.line([], [], color="green", line_width=3, alpha = 0.4)
p4ct = figure(plot_width=w2, plot_height=height)
r4ct = p4ct.line([], [], color="blue", line_width=3, alpha = 0.4)
p5ct = figure(plot_width=w2, plot_height=100)
r5_1mct  = p5ct.line([], [], color="black", line_width=1, alpha = 1.0)
r5_5mct  = p5ct.line([], [], color="black", line_width=5, alpha = 0.3)
r5_15mct = p5ct.line([], [], color="black", line_width=15, alpha = 0.1)


ps = [p1, p2, p3, p4, p5]

for pi in ps:
    pi.x_range.follow = "end"
    pi.x_range.follow_interval = 20
    pi.x_range.range_padding = 0


p1.y_range.start = 0.0
p1.y_range.end = mem_gib
p2.y_range.start = 0.
p2.y_range.end = 100.

p1ct.y_range.start = 0.0
p1ct.y_range.end = mem_gib
p2ct.y_range.start = 0.
p2ct.y_range.end = 100.

#p = vplot(p1, p2, p3, p4, p5)

#p = gridplot([[p1, p2, p3, p4, p5],[p1ct, p2ct, p3ct, p4ct, p5ct]])
#p = gridplot([[p1, p2, p3, p4, p5],[p1ct, p2ct, p3ct, p4ct, p5ct]])

p= gridplot([[p1, p1ct],
[p2, p2ct],
[p3, p3ct],
[p4, p4ct],
[p5, p5ct]])




ds1 = r1.data_source
ds1s = r1s.data_source
ds2 = r2.data_source
ds3 = r3.data_source
ds4 = r4.data_source
ds5_1m  = r5_1m.data_source
ds5_5m  = r5_5m.data_source
ds5_15m = r5_15m.data_source

ds1ct = r1ct.data_source
ds1sct = r1sct.data_source
ds2ct = r2ct.data_source
ds3ct = r3ct.data_source
ds4ct = r4ct.data_source
ds5_1mct  = r5_1mct.data_source
ds5_5mct  = r5_5mct.data_source
ds5_15mct = r5_15mct.data_source

@linear()
def update(step):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    ds1.data['x'].append(step)
    ds1.data['y'].append(float(df['used'].iloc[-1])/(1024*1024*1024))
    ds1.trigger('data', ds1.data, ds1.data)
    ds1s.data['x'].append(step)
    ds1s.data['y'].append(float(df['used.1'].iloc[-1])/(1024*1024*1024))
    ds1s.trigger('data', ds1s.data, ds1.data)
    ds2.data['x'].append(step)
    ds2.data['y'].append((100.-float(df['idl'].iloc[-1])))
    ds2.trigger('data', ds2.data, ds2.data)
    ds3.data['x'].append(step)
    ds3.data['y'].append(float(df['read'].iloc[-1])/(1024*1024))
    ds3.trigger('data', ds3.data, ds3.data)
    ds4.data['x'].append(step)
    ds4.data['y'].append(float(df['writ'].iloc[-1])/(1024*1024))
    ds4.trigger('data', ds4.data, ds4.data)
    ds5_1m.data['x'].append(step)
    ds5_1m.data['y'].append(float(df['1m'].iloc[-1]))
    ds5_1m.trigger('data', ds5_1m.data, ds5_1m.data)
    ds5_5m.data['x'].append(step)
    ds5_5m.data['y'].append(float(df['5m'].iloc[-1]))
    ds5_5m.trigger('data', ds5_5m.data, ds5_5m.data)
    ds5_15m.data['x'].append(step)
    ds5_15m.data['y'].append(float(df['15m'].iloc[-1]))
    ds5_15m.trigger('data', ds5_15m.data, ds5_15m.data)

    ds1ct.data['x'].append(step)
    ds1ct.data['y'].append(float(df['used'].iloc[-1])/(1024*1024*1024))
    ds1ct.trigger('data', ds1ct.data, ds1ct.data)
    ds1sct.data['x'].append(step)
    ds1sct.data['y'].append(float(df['used.1'].iloc[-1])/(1024*1024*1024))
    ds1sct.trigger('data', ds1sct.data, ds1ct.data)
    ds2ct.data['x'].append(step)
    ds2ct.data['y'].append((100.-float(df['idl'].iloc[-1])))
    ds2ct.trigger('data', ds2ct.data, ds2ct.data)
    ds3ct.data['x'].append(step)
    ds3ct.data['y'].append(float(df['read'].iloc[-1])/(1024*1024))
    ds3ct.trigger('data', ds3ct.data, ds3ct.data)
    ds4ct.data['x'].append(step)
    ds4ct.data['y'].append(float(df['writ'].iloc[-1])/(1024*1024))
    ds4ct.trigger('data', ds4ct.data, ds4ct.data)
    ds5_1mct.data['x'].append(step)
    ds5_1mct.data['y'].append(float(df['1m'].iloc[-1]))
    ds5_1mct.trigger('data', ds5_1mct.data, ds5_1mct.data)
    ds5_5mct.data['x'].append(step)
    ds5_5mct.data['y'].append(float(df['5m'].iloc[-1]))
    ds5_5mct.trigger('data', ds5_5mct.data, ds5_5mct.data)
    ds5_15mct.data['x'].append(step)
    ds5_15mct.data['y'].append(float(df['15m'].iloc[-1]))
    ds5_15mct.trigger('data', ds5_15mct.data, ds5_15mct.data)


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 1000)



#kk = raw_input('Working')

print 'Go terminate'
p_dstat.terminate()
print 'End program'

