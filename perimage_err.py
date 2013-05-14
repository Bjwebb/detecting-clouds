from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 
import os, sys
from django.db import reset_queries, connection

connection.close()

import math

def permonth(year, month, minimum_points=1, outdir='out', moon=True, filtered=True):

    if month == 12:
        tomonth = 1
        toyear = year+1
    else:
        tomonth = month+1
        toyear = year

    lvg = (2 if filtered else 1) if moon else (3 if filtered else 4)
    q = Image.objects.filter(
                datetime__gt=datetime.datetime(year,month,1),
                datetime__lt=datetime.datetime(toyear,tomonth,1)
                #datetime__lt=datetime.datetime(year,month,2)
                    ).order_by('datetime'
                    ).extra(select={
                    'sidlinemedianflux':'SELECT SUM(lv.median_flux) FROM clouds_sidpoint s LEFT OUTER JOIN clouds_line l ON s.line_id=l.id LEFT OUTER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND s.sidtime_id="clouds_image"."sidtime_id" AND lv.sidpoint_count>{1}'.format(lvg, minimum_points),
                    'sidlinemedianflux_squared':'SELECT SUM(lv.median_flux*lv.median_flux) FROM clouds_sidpoint s LEFT OUTER JOIN clouds_line l ON s.line_id=l.id LEFT OUTER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND s.sidtime_id="clouds_image"."sidtime_id" AND lv.sidpoint_count>{1}'.format(lvg, minimum_points),
                    'realflux':'SELECT SUM(r.flux) FROM clouds_realpoint r INNER JOIN clouds_line l ON r.line_id=l.id INNER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND r.image_id="clouds_image"."id" AND lv.sidpoint_count>{1} AND r.sidpoint_id IS NOT NULL AND r.active=true'.format(lvg, minimum_points),
                    'realflux_squared':'SELECT SUM(r.flux*r.flux) FROM clouds_realpoint r INNER JOIN clouds_line l ON r.line_id=l.id INNER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND r.image_id="clouds_image"."id" AND lv.sidpoint_count>{1} AND r.sidpoint_id IS NOT NULL AND r.active=true'.format(lvg, minimum_points),
                    }
                    )
    if not moon:
        q = q.filter(moon=False)
    for image in q: 
        realflux = image.realflux or 0.0
        realflux_squared = image.realflux_squared or 0.0
        sidlinemedianflux = image.sidlinemedianflux or 0.0
        sidlinemedianflux_squared = image.sidlinemedianflux_squared or 0.0
        try:
            visibility = realflux / sidlinemedianflux
            err = math.sqrt(realflux_squared/(realflux**2) + sidlinemedianflux_squared/(sidlinemedianflux**2))
            print image.datetime, visibility, err
        except ZeroDivisionError:
            pass
            #print image.id

    reset_queries()

class ExitError(Exception): pass
def permonth_multi(args):
    try: permonth(*args)
    except KeyboardInterrupt: raise ExitError 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Outputs values calculated per image.')
    parser.add_argument('--multi', '-m', type=int, default=0)
    parser.add_argument('--outdir', '-o', default='out') 
    cl_args = parser.parse_args()

    args = [ (year,month,minimum_points,cl_args.outdir,moon,filtered) for year in [2011,2012] for month in range(1,13) for minimum_points in [200] for moon in [True] for filtered in [True]  ]
    if cl_args.multi:
        from multiprocessing import Pool
        pool = Pool(cl_args.multi)
        try:
            result = pool.map(permonth_multi, args)
        except ExitError:
            pool.terminate()

    else:
        map(permonth_multi, args)

