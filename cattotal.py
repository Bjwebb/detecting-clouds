import numpy
import os
from PIL import Image, ImageDraw
import pandas
import math
from itertools import izip_longest

catdir = os.path.join('out', 'cat', 'sid')

from process import join, get_subdir


prev_points = None
lines_dict = {}
lines = []
steps = 0
for (path, subdirs, files) in os.walk(catdir):
    subdirs.sort()
    files.sort()

    subdir = get_subdir(path)

    for fname in files:
        if fname != 'total.cat': #FIXME
            continue
        print path

        df = pandas.read_csv(os.path.join(path, fname), delim_whitespace=True, comment='#', header=None, skiprows=12)

        df = df[ (df[7]-df[5]) < 10 ]
        df = df[ (df[8]-df[6]) < 10 ]

        points = pandas.DataFrame({ 'x': df[9], 'y': df[10] })
        aligned_points = pandas.DataFrame({ 'x': pandas.Series(), 'y': pandas.Series() })

        if prev_points is not None:
            new_lines_dict = {}
            for i, point in points.iterrows():
                distances = ((prev_points-point)**2).sum(1)
                if distances.min() < 2**2:
                    idx = distances.idxmin()
                    try:
                        new_lines_dict[i] = lines_dict[idx]
                        new_lines_dict[i].append(point)
                    except KeyError:
                        pass
                else:
                    new_lines_dict[i] = [ None ] * steps + [ point ]
                    lines.append(new_lines_dict[i])
            lines_dict = new_lines_dict
        else:
            for i, point in points.iterrows():
                lines_dict[i] = [ point ]
                lines.append(lines_dict[i])

        prev_points = points
        steps += 1
    #if steps > 10:
    #    break

"""
im = Image.new('RGB', (640,480), 'white')
draw = ImageDraw.Draw(im)
for line in lines:
    prev_point = None
    for point in line:
        if type(point) == type(None):
            continue
        if type(prev_point) == type(None):
            draw.line((point['x'], point['y'], point['x'], point['y']), fill='black')
        else:
            draw.line((prev_point['x'], prev_point['y'], point['x'], point['y']), fill='black')
        prev_point = point
im.save('cattotal.png')
"""

im = Image.new('RGB', (640,480), 'white')
draw = ImageDraw.Draw(im)

prev_points = None
for i, points in enumerate(izip_longest(*lines)):
    if type(prev_points) != type(None):
        for prev_point, point in zip(prev_points, points):
            if type(point) == type(None):
                continue
            if type(prev_point) == type(None):
                draw.line((point['x'], point['y'], point['x'], point['y']), fill='black')
            else:
                draw.line((prev_point['x'], prev_point['y'], point['x'], point['y']), fill='black')
    im.save(join('out','cattotal',str(i).zfill(4)+'.png'))
    prev_points = points
