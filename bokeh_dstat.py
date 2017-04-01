import pandas as pd
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.io import vplot
from bokeh.driving import linear
from bokeh.models import Range1d
import os
import subprocess
import time

csv_file = 'test.csv'
time_step = 1 # seconds

p_dstat = subprocess.Popen(['dstat -Tnlfvs -C total --output={0} {1}'.format(csv_file, time_step)], shell=True, stdout=open(os.devnull, 'w'))


p1 = figure(plot_width=800, plot_height=200)
r1 = p1.line([], [], color="firebrick", line_width=2)
p2 = figure(plot_width=800, plot_height=200)
r2 = p2.line([], [], color="firebrick", line_width=2)

p1.x_range.follow = "end"
p1.x_range.follow_interval = 100
p1.x_range.range_padding = 0

p2.x_range.follow = "end"
p2.x_range.follow_interval = 100
p2.x_range.range_padding = 0


p = vplot(p1, p2)


ds1 = r1.data_source
ds2 = r2.data_source

@linear()
def update(step):
    df = pd.read_csv(csv_file, index_col=False,header =0, skiprows=6)
    ds1.data['x'].append(step)
    ds1.data['y'].append(df['used'].iloc[-1])
    ds1.trigger('data', ds1.data, ds1.data)
    ds2.data['x'].append(step)
    ds2.data['y'].append(df['idl'].iloc[-1])
    ds2.trigger('data', ds1.data, ds1.data)
    #print step
    #p.x_range = bokeh.Range1d(step-100, step)
    #p.x_range.callback( Range1d(0, 100))
    #p.x_range.callback = CustomJS(args=dict(xrange=p.x_range), code="""
    #xrange.set({"start": 10, "end": 20})""")
    #p.x_range.callback = CustomJS(
    #    args=dict(source=source), code=jscode % ('x', 'width'))
    #print step, step-50, np.max([0, step-10])
    #p.x_range.end = step+10
    #p.x_range.start = step-10


curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 500)



#kk = raw_input('Working')

print 'Go terminate'
p_dstat.terminate()
print 'End program'

