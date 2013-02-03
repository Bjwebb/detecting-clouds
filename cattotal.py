import numpy, pandas
import os, datetime, math
import subprocess

catdir = os.path.join('out', 'cat', 'sid')

from process import join, get_subdir, path_split

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime 
try:
    os.remove('db.sqlite')
except OSError:
    pass
subprocess.call(['python','manage.py','syncdb'])
subprocess.call(['python','manage.py','migrate'])

prev_points_list = []
steps = 0
#points_django = []
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
                dsquared = (prev_points-point)**2
                distances = dsquared['x'] + dsquared['y']
                distance = distances.min()
                if distance < 3**2:
                    idx = distances.idxmin()
                    # This name is confusing
                    prev_point = SidPoint.objects.get(sidtime=prev_sidtime, idx=idx)
                    if prev_point.next: # then we have a collision
                        distance1 = ( (prev_point.x - prev_point.next.x)**2 + 
                                (prev_point.y - prev_point.next.y)**2 )
                        if distance < distance1:
                            discard_point = prev_point.next 
                            line = Line()
                            line.save()
                            discard_point.line = line
                            discard_point.prev = None
                            discard_point.save()
                            line = prev_point.line
                            matched = True
                    else:
                        line = prev_point.line
                        matched = True
                    break
            if not matched:
                prev_point = None
                line = Line()
                line.save()
            sidpoint = SidPoint(x=point['x'], y=point['y'], flux=point['f'], line=line, idx=i, sidtime=sidtime, prev=prev_point) 
            sidpoint.save()
        #    if len(points_django) > 1000: # Avoid sqlite variable limit #SidPoint.objects.bulk_create(points_django)
        #points_django = []

        prev_points_list.insert(0, (sidtime, points))
        if len(prev_points_list) > 4:
            prev_points_list.pop()
    steps += 1

    #if steps > 10:
    #    break
#SidPoint.objects.bulk_create(points_django)

