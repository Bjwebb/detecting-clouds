#!/usr/bin/env python
import pyfits
import numpy
from functools import partial
import scipy.misc.pilutil as smp
import sys, os, shutil, subprocess

remove_saturated = numpy.vectorize(lambda x: 0 if x < 0 or x > 65000 else x)
def flatten_max(max):
    return numpy.vectorize(lambda x: x if x < max else max)

def output(path, data, filter=False, image=False, extract=True, outdir='out'):
    if filter:
        filtered_file = os.path.join(outdir, 'fits_filtered',path)
        pyfits.writeto(filtered_file, data, clobber=True) 
        if extract:
            extfile = os.path.join(outdir, 'fits_filtered','extracted',path) 
            subprocess.call(['sextractor','-c','test.sex',filtered_file])
            shutil.move('check.fits', extfile)
            shutil.move('test.cat',
                os.path.join(outdir, 'cat', path[:-5]+'.cat')) 
            output(os.path.join('extracted',path), pyfits.getdata(extfile, 0), image=True, outdir=outdir)
    if image:
        img = smp.toimage(flatten_max(5000)(data))
        img.save(os.path.join(outdir,'png',path[:-5]+'.png'))

def process_night(orig_path, night_path, filter=True, image=True, do_output=True, do_diff=True, extraf=None, outdir='out'):
    prevdata = None
    if filter:
        if do_output:
            for a in 'fits_filtered', 'png':
                for b in '', 'extracted':
                    for c in '', 'diff':
                        if c == 'diff' and not do_diff:
                            continue
                        try:
                            os.makedirs(os.path.join(outdir,a,b,c,night_path))
                        except OSError: pass
            for c in '', 'diff':
                if c == 'diff' and not do_diff:
                    continue
                try:
                    os.makedirs(os.path.join(outdir,'cat',c,night_path))
                except OSError: pass

    for name in sorted(os.listdir(os.path.join(orig_path,night_path))):
        if not name.endswith('.fits'):
            continue
        fname = os.path.join(orig_path, night_path, name)
        hdulist = pyfits.open(fname, do_not_scale_image_data=True)
        hdu = hdulist[0] 
        data = hdu.data
        # Scale the image manually in order to use integers, not floats
        if 'BSCALE' in hdu.header and 'BZERO' in hdu.header:
            assert(hdu.header['BSCALE'] == 1)
            bzero = hdu.header['BZERO']
            data = numpy.vectorize(lambda x: x+bzero)(data)
        
        if do_diff:
            if prevdata is not None:
                if filter:
                    diff = remove_saturated( data - prevdata )
                else:
                    diff = data - prevdata
                if do_output:
                    output(os.path.join('diff',night_path,name),
                           diff, filter, image, outdir)
            prevdata = data

        if filter:
            data = remove_saturated(data)
        if extraf:
            extraf(name, data)
        if do_output:
            output(os.path.join(night_path,name),
                   data, filter, image, outdir)

def sorted_dirs(path):
    return sorted([ d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) ])


def generate_out(orig_path, extra_path='', outdir='out'):
    if extra_path:
        process_night(orig_path,
                      night_path,
                      do_diff=False,
                      outdir=outdir)
    else:
        for year in sorted_dirs(orig_path):
            for month in sorted_dirs(os.path.join(orig_path,year)):
                for night in sorted_dirs(os.path.join(orig_path,year,month)):
                    process_night(orig_path,
                                  os.path.join(year,month,night),
                                  do_diff=False,
                                  outdir=outdir)

def generate_sum(orig_path):
    for year in sorted_dirs(orig_path):
        try: int(year)
        except ValueError: continue
        day = 0
        for month in sorted_dirs(os.path.join(orig_path,year)):
            for night in sorted_dirs(os.path.join(orig_path,year,month)):
                def days(d):
                    return day + float(d[8:10])/24 + float(d[10:12])/(24*60)
                def do_sum(name, data):
                    print days(name[:-5]), numpy.sum(data, dtype=numpy.int64)
                process_night(orig_path,
                              os.path.join(year,month,night),
                              image=False,
                              do_output=False,
                              do_diff=False,
                              filter=False,
                              extraf=do_sum)
                day += 1

if __name__ == '__main__':
    orig_path = 'www.mrao.cam.ac.uk/~dfb/allsky'
    night_path = ''
    if len(sys.argv) > 2:
        night_path = sys.argv[2]

    if len(sys.argv) <= 1:
        print "Usage python process.py (out|sum) [night_path]"
    elif sys.argv[1] == 'out':
        generate_out(orig_path, night_path)
    elif sys.argv[1] == 'sum':
        generate_sum(orig_path)
