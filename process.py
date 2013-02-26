#!/usr/bin/env python
import pyfits
import numpy
import datetime, dateutil.parser, math
from operator import add
from functools import partial
import scipy.misc.pilutil as smp
import sys, os, shutil, subprocess
import json, tempfile
import errno

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image

from multiprocessing import Pool


from utils import join

def path_split(path):
    l = []
    while path:
        (path,top) = os.path.split(path)
        l.insert(0, top)
    return l

def get_subdir(path):
    return os.path.join(*path_split(path)[2:])



# Doing this to keep sextractor happy, see note in open_fits
n32 = numpy.int32
remove_saturated = numpy.vectorize(lambda x: n32(0) if x < n32(0) or x > n32(65000) else x)
def flatten_max(max):
    return numpy.vectorize(lambda x: x if x < max else max)

def open_fits(fname):
    hdulist = pyfits.open(fname, do_not_scale_image_data=True)
    hdu = hdulist[0] 
    data = hdu.data
    
    try:
        date_obs = hdu.header['DATE-OBS'] 
    except:
        date_obs = None
    
    # Scale the image manually in order to use integers, not floats
    if 'BSCALE' in hdu.header and 'BZERO' in hdu.header:
        assert(hdu.header['BSCALE'] == 1)
        # Cast to ensure data is int32s
        # Otherwise it would depend on architecture, and
        # sextractor does not like 64 bit fits files.
        bzero = numpy.int32(hdu.header['BZERO'])
        data = numpy.vectorize(lambda x: x+bzero)(data)

    return data

class DataProcessor():
    indir = 'sym'
    outdir = 'out'
    do_total = False
    do_image = True
    do_diff = False
    do_output = True
    do_filter = True
    do_extract = True
    verbose = False
    resume = True
    log = None
    log_images = None
    do_sum = False
    do_sum_db = False
    prev = []


    def __init__(self, **kwargs):
        new_args = dict((k,v) for (k,v) in kwargs.iteritems() if v is not None)

        if new_args.get('do_sum_db'):
            new_args['do_sum'] = True
        if new_args.get('do_sum'):
            self.__dict__.update(
                do_image=False,
                do_output=False,
                do_diff=False,
            )

        self.__dict__.update(new_args)

        if self.resume:
            if not self.log:
                print 'You must specify a log file in order to resume.'
                sys.exit(1)
            with open(self.log) as f:
                self.prev = f.read().splitlines()


    def extract(self, path, in_file):
        sex_file = tempfile.NamedTemporaryFile()
        checkfile = join(self.outdir,'extracted',path+'.fits')
        sex_file.write(open('template.sex').read().format(
            join(self.outdir, 'cat', path+'.cat'),
            checkfile,
            ('FULL' if self.verbose==2 else 'QUIET'),
        ))
        sex_file.flush()
        sex_file.seek(0)
        command = ['sextractor','-c',sex_file.name,in_file]
        if self.verbose == 2:
            print ' '.join(command)
        subprocess.call(command)
        self.png(os.path.join('extracted',path),
               pyfits.getdata(checkfile, 0))


    def png(self, path, data, image_filter=flatten_max(5000)):
        img = smp.toimage(image_filter(data))
        img.save(join(self.outdir,'png',path+'.png'))


    def output(self, path, data, **kwargs):
        if self.do_filter:
            filtered_file = join(self.outdir, 'fits_filtered',path+'.fits')
            if os.path.isfile(filtered_file):
                os.remove(filtered_file)
            pyfits.writeto(filtered_file, data) 

            if self.do_extract:
                self.extract(path, filtered_file)

        if self.do_image:
            self.png(path, data, **kwargs)


    def process_file(self, path):
        if not path.endswith('.fits'):
            return
        if self.verbose:
            print path
        out_path = path[:-5]
        
        data = open_fits(path) 

        if self.do_diff:
            if prevdata is not None:
                if self.do_filter:
                    data_diff = remove_saturated( data - prevdata )
                else:
                    data_diff = data - prevdata
                if do_output:
                    self.output(out_path, data_diff)

        if self.do_filter:
            data = remove_saturated(data)
        if self.do_total and numpy.sum(data, dtype=numpy.int64) < 2*(10**8):
            self.night.append(data)

        if self.do_output:
            self.output(out_path, data)
        
        if self.do_sum:
            dt = dateutil.parser.parse(os.path.basename(path).split('.')[0])
            intensity = numpy.sum(data, dtype=numpy.int64)
            print dt, intensity
            if self.do_sum_db:
                image = Image.objects.get(datetime=dt)
                image.intensity = intensity 
                image.save()

        return data


    def process_night(self, path, files):
        if self.verbose:
            print path
        if self.do_total:
            self.night = []
        if self.do_diff:
            self.prevdata = None

        for name in files:
            fpath = os.path.join(path, name)
            if self.log_images and fpath in self.prev:
                continue
            self.process_file(fpath)
            if self.log_images:
                logfile = open(self.log, 'a')
                logfile.write(fpath+'\n')
                logfile.close()

        if self.do_total and self.night:
            try:
                tdata = reduce(add, self.night)
            except ValueError, e:
                print "Encountered an error in ", indir
                print e
                return
            output(os.path.join(path, 'total'), tdata,
                image_filter=flatten_max(2000*len(night)))
        
        if self.log:
            logfile = open(self.log, 'a')
            logfile.write(path+'\n')
            logfile.close()


    def list_nights(self):
        if self.log and not self.resume:
            try:
                os.remove(self.log)
            except OSError, e:
                if e.errno != errno.ENOENT:
                    raise e
        for (path, subdirs, files) in os.walk(self.indir):
            subdirs.sort()
            files.sort()
            if not path in self.prev:
                yield(path,files)


    def process(self):
        for args in self.list_nights():
            self.process_night(*args)



def init(args_dict):
    global dp
    dp = DataProcessor(**args_dict)


class ExitError(Exception):
    pass


def process_night(args):
    global dp
    try:
        dp.process_night(*args)
    except KeyboardInterrupt:
        raise ExitError


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some all sky fits data')
    parser.add_argument('--indir', '-i')
    parser.add_argument('--outdir', '-o') 
    parser.add_argument('--verbose', '-v', action='count') 
    parser.add_argument('--multi', '-m', action='store_true') 
    parser.add_argument('--log', '-l')
    parser.add_argument('--log-images', dest='log_images', action='store_true', default=None)
    parser.add_argument('--continue', '-c', dest='resume', action='store_true') 
    for arg in ['total', 'image', 'diff', 'output', 'filter', 'extract']:
        parser.add_argument('--'+arg, dest='do_'+arg, action='store_true', default=None) 
        parser.add_argument('--no-'+arg, dest='do_'+arg, action='store_false', default=None) 
    parser.add_argument('--sum', '-s', dest='do_sum', action='store_true')
    parser.add_argument('--sum-db', '-sd', dest='do_sum', action='store_true')

    args = parser.parse_args()

    args_dict = vars(args)
    dp = DataProcessor(**args_dict)
    if dp.multi:
        from multiprocessing import Pool
        pool = Pool(4, init, (args_dict,))
        pool.map(process_night, dp.list_nights())
    else:
        dp.process()

