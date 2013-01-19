#!/usr/bin/env python
import pyfits
import numpy
import datetime, dateutil.parser, math
from functools import partial
import scipy.misc.pilutil as smp
import sys, os, shutil, subprocess
import errno

def new_path_from_datestamp(date_obs):
    return os.path.join(date_obs[0:4], date_obs[5:7], date_obs[8:10])

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
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
                  outdir='out',
                  out_path=None):
    prevdata = None

    for name in files:
        if not name.endswith('.fits'):
            continue
        fname = os.path.join(orig_path, name)
        hdulist = pyfits.open(fname, do_not_scale_image_data=True)
        hdu = hdulist[0] 
        data = hdu.data

        date_obs = hdu.header['DATE-OBS'] 
        if not out_path:
            out_path = new_path_from_datestamp(date_obs)
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

def generate_out(orig_path, outdir='out', use_path=False):
    for (path, subdirs, files) in os.walk(orig_path):
        if use_path:
            out_path = path
        else:
            out_path = None
        subdirs.sort()
        files.sort()
        process_night(path,
                      files,
                      do_diff=False,
                      outdir=outdir,
                      out_path=out_path)

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

def generate_symlinks(orig_path, outdir='sym'):
    for (path, subdirs, files) in os.walk(orig_path):
        for name in files:
            if not name.endswith('.fits'):
                continue
            fname = os.path.join(path, name)
            hdulist = pyfits.open(fname, do_not_scale_image_data=True)
            hdu = hdulist[0] 
            date_obs = hdu.header['DATE-OBS'] 
            os.symlink(os.path.abspath(fname),
                join(outdir,
                    new_path_from_datestamp(date_obs),
                    date_obs+'.fits'))

def datetime_mod(dt, divisor):
    n = int(dt.total_seconds() / divisor.total_seconds())
    return dt - n*divisor

def groupby_sidereal_time():
    orig_path = 'sym'
    sidzero = datetime.datetime(2011,1,1)
    sidday = datetime.timedelta(hours=23.9344699)
    for (path, subdirs, files) in os.walk(orig_path):
        subdirs.sort()
        files.sort()
        for fname in files:
            dt = dateutil.parser.parse(fname.split('.')[0])
            sidtime = datetime_mod(dt-sidzero, sidday)
            os.symlink(
                os.path.abspath(os.path.realpath(os.path.join(path,fname))),
                join('sid',
                    str(sidtime.seconds/3600).zfill(2),
                    str(sidtime.seconds/60).zfill(2),
                    fname))

if __name__ == '__main__':
    orig_path = 'www.mrao.cam.ac.uk/~dfb/allsky'
    if len(sys.argv) > 2:
        orig_path = sys.argv[2]

    if len(sys.argv) <= 1:
        print "Usage python process.py (out|sum|sym) [orig_path]"
    elif sys.argv[1] == 'out':
        generate_out(orig_path, use_path=True)
    elif sys.argv[1] == 'sum':
        generate_sum(orig_path)
    elif sys.argv[1] == 'sym':
        if len(sys.argv) > 3:
            generate_symlinks(orig_path, sys.argv[3])
        else:
            generate_symlinks(orig_path)
    elif sys.argv[1] == 'sid':
        groupby_sidereal_time()
