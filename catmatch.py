import numpy, pandas
import os, datetime, math
import dateutil.parser

from utils import join, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from catlib import parse_cat
from django.db import reset_queries

outdir = 'out'

def catmatch(image):
    points = parse_cat(os.path.join(outdir, 'cat', image.get_file()+'.cat'))
    if points is None:
        return

    sidtime = image.sidtime
    sidpoints = sidtime.sidpoint_set
    taken_sidpoint_ids = {}
    realpoints = []
    for i, point in points.iterrows():
        sidpoint = sidpoints.extra(select={
            'd':'pow(x-{0}, 2) + pow(y-{1}, 2)'.format(
                point['x'],point['y'])}).order_by('d')[0]
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

        realpoint = RealPoint(x=point['x'], y=point['y'],
            flux=point['flux'],
            idx=i, image=image) 
        if use_sidpoint:
            realpoint.sidpoint = sidpoint
            realpoint.line = sidpoint.line
            taken_sidpoint_ids[sidpoint.pk] = realpoint 
        realpoints.append(realpoint)
    RealPoint.objects.bulk_create(realpoints)
    
    reset_queries()

def catmatch_wrap(image):
    print image.get_file()
    try:
        catmatch(image)
    except KeyboardInterrupt:
        raise ExitError

if __name__ == '__main__':
    from multiprocessing import Pool
    pool = Pool(4)

    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("DELETE FROM clouds_realpoint")

    #pool.map(catmatch_wrap, Image.objects.filter(datetime=datetime.datetime(2012, 2, 15, 4, 30, 11)))
    pool.map(catmatch_wrap, Image.objects.all())

