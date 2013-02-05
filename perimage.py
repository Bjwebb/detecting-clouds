from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 

def scale(n): 
    s = 10000000.0 # Arbitary scaling factor to make numbers easier to compare
    try:
        return n/s
    except TypeError:
        return 0.0

for image in Image.objects.filter(datetime__lt=datetime.datetime(2011,3,20)).order_by('datetime').annotate(Sum('realpoint__flux')).annotate(Count('realpoint')):
    realpoints = image.realpoint_set.annotate(Count('line__realpoint')).filter(
        line__realpoint__count__gt=1).annotate(Avg('line__realpoint__flux')).annotate(
        Max('line__realpoint__flux'))
    fractional_flux = [ r.flux / (r.line__realpoint__flux__max) for r in realpoints ]
    comparative_flux = [ r.flux / (r.line__realpoint__flux__avg) for r in realpoints ]
    print image.datetime, (image.datetime-datetime.datetime(2011,3,1)).total_seconds(),
    print scale(image.intensity),
    if image.realpoint__flux__sum:
        print image.realpoint__flux__sum / image.realpoint__count,
    else:
        print 0.0,
    try:
        print sum(comparative_flux) / len(comparative_flux) ,
    except ZeroDivisionError:
        print 0.0,
    try:
        print sum(fractional_flux) / len(fractional_flux)
    except ZeroDivisionError:
        print 0.0

"""
for image in Image.objects.filter(datetime__lt=datetime.datetime(2011,3,2)).annotate(Sum('realpoint__flux')).annotate(
    Count('realpoint')).annotate(Count('realpoint__line__realpoint')):
    #realpoints = image.realpoint_set.annotate(Count('line__realpoint')).filter(
    #    line__realpoint__count__gt=1).annotate(Avg('line__realpoint__flux'))
    #comparative_flux = [ r.flux / (r.line__realpoint__flux__avg) for r in realpoints ]
    comparative_flux = [1]
    print image.realpoint__line__realpoint__count
    print image.datetime, image.realpoint__flux__sum / image.realpoint__count,
    print scale(image.intensity),
    print sum(comparative_flux) / len(comparative_flux)
    """
