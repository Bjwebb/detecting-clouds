from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 
import os, sys

def scale(n): 
    s = 10000000.0 # Arbitary scaling factor to make numbers easier to compare
    try:
        return n/s
    except TypeError:
        return 0.0

year = int(sys.argv[1])
month = int(sys.argv[2])
#data = open(os.path.join('out', 'sum', sys.argv[1]+sys.argv[2].zfill(2)), 'w')
data = open(os.path.join('out', 'sum2', sys.argv[1]+sys.argv[2].zfill(2)), 'w')
if month == 12:
    tomonth = 1
    toyear = year+1
else:
    tomonth = month+1
    toyear = year

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

for image in Image.objects.filter(
            datetime__gt=datetime.datetime(year,month,1),
            datetime__lt=datetime.datetime(toyear,tomonth,1)).order_by('datetime'
                ).annotate(Sum('realpoint__flux')
                ).annotate(Count('realpoint')
                ).annotate(Sum('realpoint__flux')
                ):
    realpoints = image.realpoint_set.filter(sidpoint__isnull=False).filter(
        line__average_flux__gt=0.0)#.annotate(Avg('line__realpoint__flux')).annotate(
        #Max('line__realpoint__flux'))
    out = [
        image.datetime,
        image.realpoint__count,
        len(realpoints),
        image.sidtime.sidpoint_set.count(),
        image.realpoint__flux__sum or 0.0,
        realpoints.aggregate(Sum('flux'))['flux__sum'],
        image.sidtime.sidpoint_set.aggregate(Sum('flux'))['flux__sum'],
        realpoints.aggregate(Sum('line__average_flux'))['line__average_flux__sum'],
        image.sidtime.sidpoint_set.aggregate(Sum('line__average_flux'))['line__average_flux__sum'],
    ]
    data.write( u' '.join(map(unicode, out))+u'\n' )
    data.flush()
    sys.stdout.write('.')
    sys.stdout.flush()


