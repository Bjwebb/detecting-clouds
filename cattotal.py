import numpy, pandas
import os, datetime, math
import subprocess
from PIL import Image, ImageDraw
from itertools import izip_longest

catdir = os.path.join('out', 'cat', 'sid')

from process import join, get_subdir, path_split

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime 
os.remove('db.sqlite')
subprocess.call(['python','manage.py','syncdb'])

prev_points_list = []
steps = 0
points_django = []
for (path, subdirs, files) in os.walk(catdir):
    subdirs.sort()
    files.sort()

    subdir = get_subdir(path)

    for fname in files:
        if fname != 'total.cat': #FIXME
            continue
        print path
        dirs = path_split(path)
        sidtime = SidTime(time=datetime.time(int(dirs[-2]), int(dirs[-1])))
        sidtime.save()

        df = pandas.read_csv(os.path.join(path, fname), delim_whitespace=True, comment='#', header=None, skiprows=12)

        # Exclude object larger than 10 pixels
        df = df[ (df[7]-df[5]) < 10 ]
        df = df[ (df[8]-df[6]) < 10 ]

        points = pandas.DataFrame({ 'x': df[9], 'y': df[10], 'f': df[3] })


        for i, point in points.iterrows():
            matched = False
            for prev_sidtime, prev_points in prev_points_list:
                distances = ((prev_points-point)**2).sum(1)
                if distances.min() < 3**2:
                    idx = distances.idxmin()
                    try:
                        line = SidPoint.objects.get(sidtime=prev_sidtime, idx=idx).line
                        matched = True
                    except KeyError:
                        pass
            if not matched:
                line = Line()
                line.save()
            points_django.append( SidPoint(x=point['x'], y=point['y'], flux=point['f'], line=line, idx=i, sidtime=sidtime) )
        #    if len(points_django) > 1000: # Avoid sqlite variable limit
        SidPoint.objects.bulk_create(points_django)
        points_django = []

        prev_points_list.insert(0, (sidtime, points))
        if len(prev_points_list) > 4:
            prev_points_list.pop()
        steps += 1

    #if steps > 10:
    #    break
SidPoint.objects.bulk_create(points_django)

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

