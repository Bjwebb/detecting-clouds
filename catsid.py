import numpy, pandas
import os, datetime, math
import subprocess

from process import join

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime 

from catlib import parse_cat


from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM clouds_sidpoint")
cursor.execute("DELETE FROM clouds_line")


outdir = 'out'

prev_points_list = []
steps = 0
#points_django = []
for sidtime in SidTime.objects.order_by('time'):
    siddir = os.path.join(outdir, 'cat', sidtime.get_dir())
    
    path = os.path.join(siddir, 'total.cat')
    if os.path.exists(path):
        points = parse_cat(path)
    else:
        print "{0} does not exist.".format(path)

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
        sidpoint = SidPoint(x=point['x'], y=point['y'], flux=point['flux'], line=line, idx=i, sidtime=sidtime, prev=prev_point) 
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

