from process import process_night, get_sidereal_time, output, open_fits, flatten_max
import dateutil.parser
import os, shutil

date_obs = '2011-05-25T06:00:10'

name = date_obs + '.fits'
path = os.path.join('sym', name[0:4], name[5:7], name[8:10])

files = [ name ]

process_night(path,
              files,
              do_diff=False,
              outdir='test/out',
              out_path='./',
              verbose=True)

dt = dateutil.parser.parse(name.split('.')[0])
s = get_sidereal_time(dt).seconds
path_end = os.path.join(*[ unicode(x).zfill(2) for x in [ s/3600, (s/60)%60 ] ])
fname = os.path.join('out', 'fits_filtered', 'sid', path_end, 'total.fits')
tdata = open_fits(fname)
night = os.listdir(os.path.join('sid', path_end))

for i in [100, 250, 500, 1000, 3000, 4000, 5000, 2000]:
    output('./', 'total', tdata,
        do_filter=False,
        image=True,
        extract=True,
        outdir='test/out',
        image_filter=flatten_max(i*len(night)),
        verbose=True)
    shutil.copyfile(os.path.join('test','out','png','total.png'),
            os.path.join('test', 'total{0}.png').format(i))

from django.template import Context, Template
t = Template(open(os.path.join('clouds','templates','clouds','image.html')).read())

from catlib import parse_cat

point_list = map(lambda (i,row):row, parse_cat(os.path.join('test','out','cat',date_obs+'.cat')).iterrows())
with open(os.path.join('test',date_obs+'.html'), 'w') as out:
    out.write(t.render(Context({'point_list': point_list,
                                'image': {'get_url': date_obs }
                                })))
