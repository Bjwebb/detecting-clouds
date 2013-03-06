import numpy, pandas
import os, datetime, math
import subprocess

from process import join

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import RealPoint, SidPoint, Line, SidTime 

from catlib import parse_cat

from django.db import connection, transaction, reset_queries
cursor = connection.cursor()
cursor.execute("DROP TABLE clouds_realpoint")
cursor.execute("DROP TABLE clouds_sidpoint")
cursor.execute("DROP TABLE clouds_line")
transaction.commit_unless_managed()
subprocess.call(['python', 'manage.py', 'syncdb', '--all'])

outdir = 'out'

def catsid(sidtime, prev_points_list, rerun=False):
    print 'Sidtime', sidtime
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
        step = 0
        for prev_sidtime, prev_points in prev_points_list:
            step += 1
            dsquared = (prev_points-point)**2
            distances = dsquared['x'] + dsquared['y']
            # Maybe fall back to second closest etc.
            distance = distances.min()
            if distance < 3**2:
                idx = distances.idxmin()
                # This name is confusing
                try:
                    prev_point = SidPoint.objects.get(sidtime=prev_sidtime, idx=idx)
                except SidPoint.DoesNotExist, e:
                    #break
                    raise e
                competing_point = prev_point.next 
                if competing_point: # then we have a collision
                    if competing_point.step >= i:
                        distance1 = ( (prev_point.x - competing_point.x)**2 + 
                                (prev_point.y - competing_point.y)**2 )
                        if distance < distance1:
                            line = Line()
                            line.save()
                            competing_point.line = line
                            competing_point.prev = None
                            competing_point.save()
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
            step = None
            line = Line()
            line.save()
        if rerun:
            sidpoint.prev = prev_point
            if sidpoint.line != line:
                sidpoint.line.sidpoint_set.update(line=line)
                sidpoint.line.delete()
                sidpoint.line = line
        else:
            sidpoint = SidPoint(
                x=point['x'], y=point['y'],
                x_min=point['x_min'], y_min=point['y_min'],
                width=point['width'], height=point['height'],
                flux=point['flux'],
                line=line, idx=i, sidtime=sidtime, prev=prev_point, step=step) 
        sidpoint.save()

    reset_queries()

    if not rerun:
        prev_points_list.insert(0, (sidtime, points))
    if rerun or len(prev_points_list) > 4:
        prev_points_list.pop()

sidtimes = list(SidTime.objects.order_by('time'))
prev_points_list = []
"""
for sidtime in sidtimes[:4]:
    catsid(sidtime, prev_points_list)
prev_points_list = []
for sidtime in sidtimes[-5:]:
    catsid(sidtime, prev_points_list)
"""
for sidtime in sidtimes:
    catsid(sidtime, prev_points_list)
for sidtime in sidtimes[:4]:
    catsid(sidtime, prev_points_list, True)
print prev_points_list



