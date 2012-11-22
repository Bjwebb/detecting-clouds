#!/usr/bin/env python
import pyfits
import numpy
from functools import partial
import scipy.misc.pilutil as smp
import os
#path = 'www.mrao.cam.ac.uk/~dfb/allsky/2011/06/20110601'
#path = './'
path = 'extracted/filtered'
#print pyfits.info(fname)
prevdata = None


max = 5000 
trim_values = numpy.vectorize(lambda x: 0 if x > 65000 else x if x < max else max)
trim_values2 = numpy.vectorize(lambda x: 0 if x > 65000 or x < 0 else x if x < max else max)

for name in sorted(os.listdir(path)):
    if not name.endswith('.fits'):
        continue
    fname = os.path.join(path, name)
    data = pyfits.getdata(fname, 0)
    
    if prevdata is not None:
        diff = data - prevdata
        img = smp.toimage(trim_values2(diff))
        img.save(os.path.join('diff', name[:-5]+'.png'))
    #prevdata = data

    data = trim_values(data)
    img = smp.toimage(data)
    img.save(os.path.join('out', 'extracted', name[:-5]+'.png'))
