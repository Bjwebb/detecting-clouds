import numpy, pandas
import os, datetime, math
import dateutil.parser, subprocess

from utils import join, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime, RealPointGeneration 
from catlib import parse_cat
from django.db import reset_queries, transaction

outdir = 'out'
generation_pk = 1

def catmatch(image):
    global generation_pk
    generation, created = RealPointGeneration.objects.get_or_create(pk=generation_pk)

    points = parse_cat(os.path.join(outdir, 'cat', image.get_file()+'.cat'))
    if points is None:
        return

    sidtime = image.sidtime
    sidpoints = sidtime.sidpoint_set
    taken_sidpoint_ids = {}
    realpoints = []
    for i, point in points.iterrows():
        try:
            sidpoint = sidpoints.extra(select={
                'd':'pow(x-{0}, 2) + pow(y-{1}, 2)'.format(
                    point['x'],point['y'])}).order_by('d')[0]
        except IndexError:
            continue
        if sidpoint.d < 3**2:
            use_sidpoint = True
            if sidpoint.pk in taken_sidpoint_ids:
                other_realpoint = taken_sidpoint_ids[sidpoint.pk]
                distance1 = (other_realpoint.x - sidpoint.x)**2 + (other_realpoint.y - sidpoint.y)**2
                if sidpoint.d < distance1:
                    other_realpoint.sidpoint = None
                else:
                    use_sidpoint = False
        else:
            use_sidpoint = False

        realpoint = RealPoint(
            x=point['x'], y=point['y'],
            x_min=point['x_min'], y_min=point['y_min'],
            width=point['width'], height=point['height'],
            flux=point['flux'], flux_error=point['flux_error'],
            idx=i, image=image, generation=generation) 
        if use_sidpoint:
            realpoint.sidpoint = sidpoint
            realpoint.line = sidpoint.line
            taken_sidpoint_ids[sidpoint.pk] = realpoint 
        realpoints.append(realpoint)
    RealPoint.objects.bulk_create(realpoints)
    
    reset_queries()

def catmatch_wrap(image):
    print image.pk, image.get_file()
    try:
        catmatch(image)
    except KeyboardInterrupt:
        raise ExitError

if __name__ == '__main__':
    from django.db import connection
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
    ##start = start + datetime.timedelta(hours=10)
    #pool.map(catmatch_wrap, Image.objects.filter(datetime__lt=end, datetime__gt=start))

