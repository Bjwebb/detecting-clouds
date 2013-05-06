from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 
import os, sys
from django.db import reset_queries, connection

def scale(n): 
    s = 10000000.0 # Arbitary scaling factor to make numbers easier to compare
    try:
        return n/s
    except TypeError:
        return 0.0


connection.close()


def permonth(year, month, minimum_points=1, generation=1, outdir='out', moon=True):

    if month == 12:
        tomonth = 1
        toyear = year+1
    else:
        tomonth = month+1
        toyear = year

    dirname = 'sum{0}-{1}{2}'.format(minimum_points, generation, '' if moon else '-nomoon')
    try:
        os.mkdir(os.path.join(outdir, dirname))
    except OSError:
        pass
    data = open(os.path.join(outdir, dirname, str(year)+str(month).zfill(2)), 'w')

    lvg = 2 if moon else 3
    q = Image.objects.filter(
                datetime__gt=datetime.datetime(year,month,1),
                datetime__lt=datetime.datetime(toyear,tomonth,1)
                    ).order_by('datetime'
                    ).extra(select={
                    'sidlinemaxflux':'SELECT SUM(lv.max_flux) FROM clouds_sidpoint s LEFT OUTER JOIN clouds_line l ON s.line_id=l.id LEFT OUTER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND s.sidtime_id="clouds_image"."sidtime_id" AND lv.sidpoint_count>{1}'.format(lvg, minimum_points),
                    'sidlinemedianflux':'SELECT SUM(lv.median_flux) FROM clouds_sidpoint s LEFT OUTER JOIN clouds_line l ON s.line_id=l.id LEFT OUTER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND s.sidtime_id="clouds_image"."sidtime_id" AND lv.sidpoint_count>{1}'.format(lvg, minimum_points),
                    'realflux':'SELECT SUM(r.flux) FROM clouds_realpoint r INNER JOIN clouds_line l ON r.line_id=l.id INNER JOIN  clouds_linevalues lv ON lv.line_id=l.id WHERE lv.generation_id={0} AND r.image_id="clouds_image"."id" AND lv.sidpoint_count>{1} AND r.sidpoint_id IS NOT NULL AND r.active=true'.format(lvg, minimum_points),
                    }
                    )
    if not moon:
        q = q.filter(moon=False)
    for image in q: 
        #kwargs = dict(line__linevalues__generation__pk=lvg, line__linevalues__sidpoint_count__gt=minimum_points)
    
        #realpoints = image.realpoint_set.filter(generation=generation, sidpoint__isnull=False,
        #    active=True, **kwargs)
        #realflux = realpoints.filter(generation=generation).aggregate(Sum('flux'))['flux__sum'] or 0.0
        #sidlinemedianflux = image.sidtime.sidpoint_set.filter(**kwargs).aggregate(Sum('line__linevalues__median_flux'))['line__linevalues__median_flux__sum'] 
        #sidlinemaxflux = image.sidtime.sidpoint_set.filter(**kwargs).aggregate(Sum('line__linevalues__max_flux'))['line__linevalues__max_flux__sum'] 
        realflux = image.realflux or 0.0
        sidlinemaxflux = image.sidlinemaxflux or 0.0
        sidlinemedianflux = image.sidlinemedianflux or 0.0
        try:
            out = [
                # 1
                image.datetime,
                # 3
                realflux/sidlinemaxflux,
                # 4
                realflux/sidlinemedianflux,
                # 5
                image.intensity,
                # 6
                realflux,
                # 7
                sidlinemedianflux,
                # 8
                sidlinemaxflux,
            ]
            data.write( u' '.join(map(unicode, out))+u'\n' )
            data.flush()
        except ZeroDivisionError:
            print image.id

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

    args = [ (year,month,minimum_points,generation,cl_args.outdir,moon) for year in [2011,2012] for month in range(1,13) for minimum_points in [1,20,200] for generation in [1] for moon in [True,False]  ]
    if cl_args.multi:
        from multiprocessing import Pool
        pool = Pool(cl_args.multi)
        try:
            result = pool.map(permonth_multi, args)
        except ExitError:
            pool.terminate()

    else:
        map(permonth_multi, args)

