import numpy
import os
from PIL import Image, ImageDraw
import pandas
import math
from itertools import izip_longest
import json

catdir = os.path.join('out', 'cat', 'sid')

from process import join, get_subdir


prev_points_list = []
prev_lines_dict_list = []
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

        # Exclude object larger than 10 pixels
        df = df[ (df[7]-df[5]) < 10 ]
        df = df[ (df[8]-df[6]) < 10 ]

        points = pandas.DataFrame({ 'x': df[9], 'y': df[10], 'f': df[3] })

        lines_dict = {}
        for i, point in points.iterrows():
            matched = False
            for prev_points, prev_lines_dict in zip(prev_points_list, prev_lines_dict_list):
                distances = ((prev_points-point)**2).sum(1)
                if distances.min() < 3**2:
                    idx = distances.idxmin()
                    try:
                        lines_dict[i] = prev_lines_dict[idx]
                        lines_dict[i].append(dict(point))
                        del prev_lines_dict[idx]
                        matched = True
                    except KeyError:
                        pass
            if not matched:
                lines_dict[i] = [ None ] * steps + [ dict(point) ]
                lines.append(lines_dict[i])

        prev_points_list.insert(0, points)
        prev_lines_dict_list.insert(0, lines_dict)
        if len(prev_points_list) > 4:
            prev_points_list.pop()
            prev_lines_dict_list.pop()
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
"""

json.dump(lines, open(os.path.join('out', 'lines.json'), 'w')) 
