#!/usr/bin/env python
import pyfits
import numpy
from functools import partial
import scipy.misc.pilutil as smp
import sys, os, shutil, subprocess
import errno

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Calls os.path.join, but also ensures the directory exists
def join(*args):
    ensure_dir_exists(os.path.join(*args[:-1])) 
    return os.path.join(*args)

remove_saturated = numpy.vectorize(lambda x: 0 if x < 0 or x > 65000 else x)
def flatten_max(max):
    return numpy.vectorize(lambda x: x if x < max else max)

def output(path, name, data, filter=False, image=False, extract=True, outdir='out'):
    if filter:
        filtered_file = join(outdir, 'fits_filtered',path, name+'.fits')
        pyfits.writeto(filtered_file, data, clobber=True) 
        if extract:
            extfile = join(outdir, 'fits_filtered','extracted',path, name+'.fits')
            subprocess.call(['sextractor','-c','test.sex',filtered_file])
            shutil.move('check.fits', extfile)
            shutil.move('test.cat', join(outdir, 'cat', path, name+'.cat')) 
            output(os.path.join('extracted',path),
                   name,
                   pyfits.getdata(extfile, 0),
                   image=True, outdir=outdir)
    if image:
        img = smp.toimage(flatten_max(5000)(data))
        img.save(join(outdir,'png',path, name+'.png'))

def process_night(orig_path,
                  files,
                  filter=True,
                  image=True,
                  do_output=True,
                  do_diff=True,
                  extraf=None,
                  outdir='out'):
    prevdata = None

    for name in files:
        if not name.endswith('.fits'):
            continue
        fname = os.path.join(orig_path, name)
        hdulist = pyfits.open(fname, do_not_scale_image_data=True)
        hdu = hdulist[0] 
        data = hdu.data

        date_obs = hdu.header['DATE-OBS'] 
        out_path = os.path.join(date_obs[0:4], date_obs[5:7], date_obs[8:10])
        out_name = date_obs

        # Scale the image manually in order to use integers, not floats
        if 'BSCALE' in hdu.header and 'BZERO' in hdu.header:
            assert(hdu.header['BSCALE'] == 1)
            bzero = hdu.header['BZERO']
            data = numpy.vectorize(lambda x: x+bzero)(data)
        
        if do_diff:
            if prevdata is not None:
                if filter:
                    data_diff = remove_saturated( data - prevdata )
                else:
                    data_diff = data - prevdata
                if do_output:
                    output(os.path.join('diff',out_path),
                           out_name,
                           data_diff, filter, image, outdir)
            prevdata = data

        if filter:
            data = remove_saturated(data)
        if extraf:
            extraf(name, data)
        if do_output:
            output(out_path, out_name, data, filter, image, outdir)

def generate_out(orig_path, outdir='out'):
    for (path, subdirs, files) in os.walk(orig_path):
        process_night(path,
                      files,
                      do_diff=False,
                      outdir=outdir)

def generate_sum(orig_path):
    day = 0
    def days(d):
        return day + float(d[8:10])/24 + float(d[10:12])/(24*60)
    def do_sum(name, data):
        print days(name[:-5]), numpy.sum(data, dtype=numpy.int64)

    for (path, subdirs, files) in os.walk(orig_path):
        subdirs.sort()
        files.sort()
        process_night(path,
                      files,
                      image=False,
                      do_output=False,
                      do_diff=False,
                      filter=False,
                      extraf=do_sum)
    day += 1

if __name__ == '__main__':
    orig_path = 'www.mrao.cam.ac.uk/~dfb/allsky'
    if len(sys.argv) > 2:
        orig_path = sys.argv[2]

    if len(sys.argv) <= 1:
        print "Usage python process.py (out|sum) [orig_path]"
    elif sys.argv[1] == 'out':
        generate_out(orig_path)
    elif sys.argv[1] == 'sum':
        generate_sum(orig_path)
