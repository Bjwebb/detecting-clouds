import numpy
import os
from PIL import Image, ImageDraw

catdir = os.path.join('out', 'cat', 'sid')

from process import join, get_subdir


for (path, subdirs, files) in os.walk(catdir):
    subdirs.sort()
    files.sort()

    tot = Image.new('RGB', (640,480), 'white')
    tdraw = ImageDraw.Draw(tot)
    subdir = get_subdir(path)
    for fname in files:
        print fname
        im = Image.open(os.path.join('out','png',subdir,fname[:-4]+'.png')).convert('RGB')

        draw = ImageDraw.Draw(im)
        for row in numpy.genfromtxt(os.path.join(path, fname)):
            a1,a2,a3,a4,xmin,ymin,xmax,ymax, x, y, flags = row
            if (ymax-ymin) < 10 and (xmax-xmin) < 10:
                draw.rectangle((xmin,ymin,xmax,ymax), outline='red')
                tdraw.rectangle((xmin,ymin,xmax,ymax), outline='red', fill='red')
        im.save(join('out','post',subdir,fname[:-4]+'.png'))
    tot.save(join('out','post',subdir,'cat_total.png'))
