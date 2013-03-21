import numpy, pandas
import os, datetime, math
import dateutil.parser, subprocess

from utils import join, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime, RealPointGeneration
from catlib import parse_cat
from django.db import reset_queries, connection, transaction

outdir = 'out'
generation_pk = 6
copy_generation_pk = 4

def catreal(image):
    global generation_pk
    generation, created = RealPointGeneration.objects.get_or_create(pk=generation_pk)
    points = parse_cat(os.path.join(outdir, 'cat', image.get_file()+'.cat'))
    if points is None:
        return

    realpoints = []
    for realpoint in image.realpoint_set.filter(generation=copy_generation_pk):
        point = points.ix[realpoint.idx]
        realpoint.pk = None
        realpoint.id = None
        realpoint.flux = point['flux']
        realpoint.flux_error = point['flux_error']
        realpoint.generation = generation
        realpoints.append(realpoint)
    RealPoint.objects.bulk_create(realpoints)
    
    reset_queries()

def catreal_wrap(image):
    print image.get_file()
    try:
        catreal(image)
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

    #map(catreal_wrap, Image.objects.all())
    #pool.map(catreal_wrap, Image.objects.all())
    import datetime
    start = datetime.datetime(2011,8,23)
    end = start + datetime.timedelta(days=1)
    pool.map(catreal_wrap, Image.objects.filter(datetime__lt=end, datetime__gt=start))
