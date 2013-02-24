import numpy
import os
from PIL import Image, ImageDraw
import sys

#catdir = os.path.join('out', 'cat', 'sid')
catdir = sys.argv[1]

from process import join, get_subdir


for (path, subdirs, files) in os.walk(catdir):
    subdirs.sort()
    files.sort()

    tot = Image.new('RGB', (640,480), 'white')
    tdraw = ImageDraw.Draw(tot)
    postdir = catdir.replace('cat','post')
    for fname in files:
        im = Image.open(os.path.join(catdir.replace('cat','png'),fname[:-4]+'.png')).convert('RGB')

        draw = ImageDraw.Draw(im)
        for row in numpy.genfromtxt(os.path.join(path, fname)):
            a1,a2,a3,a4,xmin,ymin,xmax,ymax, x, y, flags = row
            if (ymax-ymin) < 10 and (xmax-xmin) < 10:
                draw.rectangle((xmin,ymin,xmax,ymax), outline='red')
                tdraw.rectangle((xmin,ymin,xmax,ymax), outline='red', fill='red')
        im.save(join(postdir,fname[:-4]+'.png'))
    tot.save(join(postdir,'cat_total.png'))
