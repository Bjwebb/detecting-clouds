from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 
import os, sys
from django.db import reset_queries, connection

from process import open_fits
import numpy
import scipy.misc.pilutil as smp

imgs = numpy.dstack(
    [
        open_fits(os.path.join('out', 'fits_filtered', image.get_file()+'.fits'))
        for image in Image.objects.filter(moon=False)[:1000]
    ])

median = numpy.percentile(imgs, 10, axis=2) 
img = smp.toimage(median)#, cmax=3000)
img.save('pixelimage.png')
