import numpy, pandas
import os, datetime, math
import subprocess

from process import join

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime 

from catlib import parse_cat

from django.db import connection, transaction
cursor = connection.cursor()
#cursor.execute("DELETE FROM clouds_realpoint")
cursor.execute("DELETE FROM clouds_sidpoint")
cursor.execute("DELETE FROM clouds_line")
transaction.commit_unless_managed()

outdir = 'out'

def catsid(sidtime, prev_points_list, rerun=False):
    print sidtime
    siddir = os.path.join(outdir, 'cat', sidtime.get_dir())
    
    path = os.path.join(siddir, 'total.cat')
    if os.path.exists(path):
        points = parse_cat(path)
    else:
        print "{0} does not exist.".format(path)
        return

    for i, point in points.iterrows():
        #if i > 30:
        #    break
        if rerun:
            sidpoint = SidPoint.objects.get(sidtime=sidtime, idx=i)
            if sidpoint.prev:
                continue
        matched = False
        for prev_sidtime, prev_points in prev_points_list:
            dsquared = (prev_points-point)**2
            distances = dsquared['x'] + dsquared['y']
            distance = distances.min()
            if distance < 3**2:
                idx = distances.idxmin()
                # This name is confusing
                try:
                    prev_point = SidPoint.objects.get(sidtime=prev_sidtime, idx=idx)
                except SidPoint.DoesNotExist, e: raise e #continue
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
            if rerun:
                continue
            prev_point = None
            line = Line()
            line.save()
        if rerun:
            sidpoint.prev = prev_point
            sidpoint.line.sidpoint_set.update(line=line)
            sidpoint.line.delete()
            sidpoint.line = line
        else:
            sidpoint = SidPoint(x=point['x'], y=point['y'], flux=point['flux'], line=line, idx=i, sidtime=sidtime, prev=prev_point) 
        sidpoint.save()
    #    if len(points_django) > 1000: # Avoid sqlite variable limit #SidPoint.objects.bulk_create(points_django)
    #points_django = []

    if not rerun:
        prev_points_list.insert(0, (sidtime, points))
        if len(prev_points_list) > 4:
            prev_points_list.pop()

sidtimes = list(SidTime.objects.order_by('time'))
prev_points_list = []
for sidtime in sidtimes:
    catsid(sidtime, prev_points_list)
for sidtime in sidtimes[:4]:
    catsid(sidtime, prev_points_list, True)


#SidPoint.objects.bulk_create(points_django)

