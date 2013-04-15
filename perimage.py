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


"""
for image in Image.objects.filter(
            datetime__gt=datetime.datetime(year,month,1),
            datetime__lt=datetime.datetime(toyear,tomonth,1)).order_by('datetime').annotate(Sum('realpoint__flux')).annotate(Count('realpoint')):
    realpoints = image.realpoint_set.annotate(Count('line__realpoint')).filter(
        line__realpoint__count__gt=1).annotate(Avg('line__realpoint__flux')).annotate(
        Max('line__realpoint__flux'))
    fractional_flux = [ r.flux / (r.line__realpoint__flux__max) for r in realpoints ]
    comparative_flux = [ r.flux / (r.line__realpoint__flux__avg) for r in realpoints ]
    out = [ unicode(image.datetime) ]
    out.append(unicode( (image.datetime-datetime.datetime(2011,3,1)).total_seconds() ))
    out.append(unicode( scale(image.intensity) ))
    if image.realpoint__flux__sum:
        out.append(unicode( image.realpoint__flux__sum ))
    else:
        out.append(unicode( 0.0 ))
    try:
        out.append(unicode( sum(comparative_flux) / len(comparative_flux) ))
    except ZeroDivisionError:
        out.append(unicode( 0.0 ))
    try:
        out.append(unicode( sum(fractional_flux) / len(fractional_flux) ))
    except ZeroDivisionError:
        out.append(unicode( 0.0 ))
    out.append(unicode( sum(comparative_flux) ))
    out.append(unicode( sum(fractional_flux) ))
    out.append(unicode( len(realpoints) ))
    out.append(unicode( image.realpoint__count ))
    data.write( u' '.join(out)+u'\n' )
    data.flush()
    sys.stdout.write('.')
    sys.stdout.flush()
"""

def permonth(year, month, minimum_points=1, generation=1, outdir='out'):

    if month == 12:
        tomonth = 1
        toyear = year+1
    else:
        tomonth = month+1
        toyear = year

    try:
        os.mkdir(os.path.join(outdir, 'sum{0}-{1}'.format(minimum_points, generation)))
    except OSError:
        pass
    data = open(os.path.join(outdir, 'sum{0}-{1}'.format(minimum_points, generation), str(year)+str(month).zfill(2)), 'w')

    for image in Image.objects.filter(
                datetime__gt=datetime.datetime(year,month,1),
                datetime__lt=datetime.datetime(toyear,tomonth,1),
                realpoint__generation=generation
                    ).order_by('datetime'
                    ).annotate(Sum('realpoint__flux')
                    ).annotate(Count('realpoint')
                    ).annotate(Sum('realpoint__flux')
                    ):
        kwargs = dict(line__linevalues__generation__pk=3, line__linevalues__realpoint_count__gt=minimum_points)
    
        realpoints = image.realpoint_set.filter(generation=generation, sidpoint__isnull=False,
            active=True, **kwargs)
        realflux = realpoints.filter(generation=generation).aggregate(Sum('flux'))['flux__sum'] or 0.0
        sidlineaverageflux = image.sidtime.sidpoint_set.filter(**kwargs).aggregate(Sum('line__linevalues__average_flux'))['line__linevalues__average_flux__sum'] 
        sidlinemaxflux = image.sidtime.sidpoint_set.filter(**kwargs).aggregate(Sum('line__linevalues__max_flux'))['line__linevalues__max_flux__sum'] 
        out = [
            # 1
            image.datetime,
            # 3
            realflux/sidlinemaxflux,
            # 4
            realflux/sidlineaverageflux,
            # 5
            image.realpoint__count,
            # 6
            len(realpoints),
            # 7
            image.sidtime.sidpoint_set.count(),
            # 8
            scale(image.intensity),
            # 9
            scale(image.realpoint__flux__sum),
            # 10
            realflux,
            # 11
            image.sidtime.sidpoint_set.aggregate(Sum('flux'))['flux__sum'],
            # 12
            realpoints.aggregate(Sum('line__linevalues__average_flux'))['line__linevalues__average_flux__sum'],
            # 13
            sidlinemaxflux,
            # 14
            sidlineaverageflux,
        ]
        data.write( u' '.join(map(unicode, out))+u'\n' )
        data.flush()
        sys.stdout.write('.')
        sys.stdout.flush()

    reset_queries()

class ExitError(Exception): pass
def permonth_multi(args):
    try: permonth(*args)
    except KeyboardInterrupt: raise ExitError 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Outputs values calculated per image.')
    parser.add_argument('--multi', '-m', type=int, default=0)
    parser.add_argument('--outdir', '-o') 
    cl_args = parser.parse_args()

    args = [ (year,month,minimum_points,generation,cl_args.outdir) for year in [2011,2012] for month in range(1,13) for minimum_points in [1] for generation in [1]  ]
    if cl_args.multi:
        from multiprocessing import Pool
        pool = Pool(cl_args.multi)
        try:
            result = pool.map(permonth_multi, args)
        except ExitError:
            pool.terminate()

    else:
        map(permonth_multi, args)
        #year = int(sys.argv[1])
        #month = int(sys.argv[2])
        #permonth(year, month)

