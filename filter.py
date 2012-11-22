#!/usr/bin/env python
import pyfits
import numpy
import os
path = 'www.mrao.cam.ac.uk/~dfb/allsky/2011/06/20110601'
prevdata = None

trim_values = numpy.vectorize(lambda x: 0 if x > 65000 else x)
trim_values2 = numpy.vectorize(lambda x: 0 if x < 0 or x > 65000 else x)

for name in sorted(os.listdir(path)):
    if not name.endswith('.fits'):
        continue
    fname = os.path.join(path, name)
    header = pyfits.getheader(fname)
    data = pyfits.getdata(fname, 0)

    if prevdata is not None:
        diff = trim_values2( data - prevdata )
        pyfits.writeto('diff.fits', diff)
        break
    #prevdata = data

    data = trim_values(data)
    pyfits.writeto(os.path.join('filtered', name[:-5]+'.fits'), data)

