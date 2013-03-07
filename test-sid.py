from utils import get_sidereal_time
from process import open_fits, flatten_max, DataProcessor
import dateutil.parser
import os, shutil

dp = DataProcessor()
dp.outdir = 'test/out'
dp.verbose = 1

st = '0429'
path_end = os.path.join(st[0:2], st[2:4])
path = os.path.join('sid', path_end)
night = os.listdir(path)

dp.do_total = True
dp.indir = 'sid'
dp.do_filter = False
dp.do_output = False
dp.process_night(path, night)

from django.template import Context, Template
t = Template(open(os.path.join('clouds','templates','clouds','image.html')).read())

from catlib import parse_cat

point_list = map(lambda (i,row):row, parse_cat(os.path.join('test', 'out', 'cat', path, 'total.cat')).iterrows())
print len(point_list)
with open(os.path.join('test',st+'.html'), 'w') as out:
    out.write(t.render(Context({'point_list': point_list,
                                'point_pk': -1,
                                'object': {'get_url': path+'/total' }
                                })))
