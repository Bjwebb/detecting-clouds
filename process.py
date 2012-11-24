#!/usr/bin/env python
import pyfits
import numpy
from functools import partial
import scipy.misc.pilutil as smp
import os, shutil, subprocess
orig_path = 'www.mrao.cam.ac.uk/~dfb/allsky'

remove_saturated = numpy.vectorize(lambda x: 0 if x < 0 or x > 65000 else x)
def flatten_max(max):
    return numpy.vectorize(lambda x: x if x < max else max)

def output(path, data, filter=False, image=False, extract=True):
    if filter:
        filtered_file = os.path.join('filtered',path)
        pyfits.writeto(filtered_file, data)
        if extract:
            extfile = os.path.join('filtered','extracted',path) 
            subprocess.call(['sextractor','-c','test.sex',filtered_file])
            shutil.move('check.fits', extfile)
            output(os.path.join('extracted',path), pyfits.getdata(extfile, 0), image=True)
    if image:
        img = smp.toimage(flatten_max(5000)(data))
        img.save(os.path.join('out',path[:-5]+'.png'))

def process_night(orig_path, night_path, filter=True, image=True):
    prevdata = None
    if filter:
        for a in 'filtered', 'out':
            for b in '', 'extracted':
                for c in '', 'diff':
                    os.makedirs(os.path.join(a,b,c,night_path))

    for name in sorted(os.listdir(os.path.join(orig_path,night_path))):
        if not name.endswith('.fits'):
            continue
        fname = os.path.join(orig_path, night_path, name)
        header = pyfits.getheader(fname)
        data = pyfits.getdata(fname, 0)


        if prevdata is not None:
            diff = remove_saturated( data - prevdata )
            output(os.path.join('diff',night_path,name),
                   diff, filter, image)
        prevdata = data

        data = remove_saturated(data)
        output(os.path.join(night_path,name),
               data, filter, image)

for directory in ['filtered', 'out']:
    try:
        shutil.rmtree(directory)
    except OSError:
        pass

def sorted_dirs(path):
    return sorted([ d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) ])

for year in sorted_dirs(orig_path):
    for month in sorted_dirs(os.path.join(orig_path,year)):
        for night in sorted_dirs(os.path.join(orig_path,year,month)):
            process_night(orig_path, os.path.join(year,month,night))

