import numpy, pandas
import os, datetime, math
import dateutil.parser, subprocess

from utils import join, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime, RealPointGeneration 
from catlib import parse_cat, in_mask
from django.db import reset_queries, transaction, connection

outdir = 'out'
generation_pk = 1

def catmatch(image):
    global generation_pk
    generation, created = RealPointGeneration.objects.get_or_create(pk=generation_pk)

    points = parse_cat(os.path.join(outdir, 'cat', image.get_file()+'.cat'))
    if points is None:
        return

    realpoints = []
    for i, point in points.iterrows():
        if not in_mask(point):
            continue
        realpoint = RealPoint(
            x=point['x'], y=point['y'],
            x_min=point['x_min'], y_min=point['y_min'],
            width=point['width'], height=point['height'],
            flux=point['flux'], flux_error=point['flux_error'],
            idx=i, image=image, generation=generation) 
        realpoints.append(realpoint)
    RealPoint.objects.bulk_create(realpoints)

    cursor = connection.cursor()
    cursor.execute('UPDATE clouds_realpoint r SET sidpoint_id=(SELECT id FROM clouds_sidpoint WHERE sidtime_id=%s AND x>r.x-5 AND x<r.x+5 AND y>r.y-5 AND y<r.y+5 AND POW(x-r.x,2)+POW(y-r.y,2) < 9 ORDER BY POW(x-r.x,2)+POW(y-r.y,2) ASC LIMIT 1) WHERE r.image_id=%s', (image.sidtime_id,image.id,))
    cursor.execute('SELECT r.id, sidpoint_id, POW(s.x-r.x,2)+POW(s.y-r.y,2) AS d FROM clouds_realpoint r JOIN clouds_sidpoint s ON s.id=r.sidpoint_id WHERE sidpoint_id IN (SELECT sidpoint_id FROM clouds_realpoint GROUP BY sidpoint_id HAVING COUNT(sidpoint_id)>1) AND r.image_id=%s ORDER BY d ASC', (image.id,))
    done = {}
    null = []
    while True:
        row = cursor.fetchone()
        if not row: break
        if row[1] in done:
            null.append(str(row[0]))
        else:
            done[row[1]] = 0
    if null:
        cursor.execute('UPDATE clouds_realpoint SET sidpoint_id=NULL WHERE id IN ({0})'.format(','.join(null)))
    cursor.execute('UPDATE clouds_realpoint r SET line_id=(SELECT line_id FROM clouds_sidpoint WHERE id=r.sidpoint_id) WHERE r.image_id=%s', (image.id,))

    reset_queries()

def catmatch_wrap(image):
    print image.pk, image.get_file()
    try:
        catmatch(image)
    except KeyboardInterrupt:
        raise ExitError

if __name__ == '__main__':
    cursor = connection.cursor()
    cursor.execute("DELETE FROM clouds_realpoint WHERE generation_id=%s", [generation_pk])
    transaction.commit_unless_managed()

    connection.close()

    from multiprocessing import Pool
    pool = Pool(4)

    pool.map(catmatch_wrap, Image.objects.order_by('datetime'))

    #import datetime
    #start = datetime.datetime(2011,8,23)
    #end = start + datetime.timedelta(days=1)
    #pool.map(catmatch_wrap, Image.objects.filter(datetime__lt=end, datetime__gt=start))

