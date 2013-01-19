import numpy
import os
from PIL import Image, ImageDraw

catdir = os.path.join('out', 'cat', 'sid')

from process import join

def path_split(path):
    l = []
    while path:
        (path,top) = os.path.split(path)
        l.insert(0, top)
    return l


for (path, subdirs, files) in os.walk(catdir):
    for fname in files:
        subdir = os.path.join(*path_split(path)[2:])
        im = Image.open(os.path.join('out','png',subdir,fname[:-4]+'.png')).convert('RGB')
        print im.mode
        draw = ImageDraw.Draw(im)
        for row in numpy.genfromtxt(os.path.join(path, fname)):
            a1,a2,a3,a4,xmin,ymin,xmax,ymax, x, y, flags = row
            if (ymax-ymin) < 30 and (xmax-xmin) < 30:
                draw.rectangle((xmin,ymin,xmax,ymax), outline='red')
        im.save(join('out','post',subdir,fname[:-4]+'.png'))
