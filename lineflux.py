from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg, StdDev

for line in Line.objects.annotate(
        Count('realpoint'),
        Avg('realpoint__flux'),
        StdDev('realpoint__flux', sample=True),
        Max('realpoint__flux')
        ):
    line.realpoint_count = line.realpoint__count
    line.average_flux = line.realpoint__flux__avg or 0.0
    line.stddev_flux = line.realpoint__flux__stddev or 0.0
    line.max_flux = line.realpoint__flux__max or 0.0
    line.save()
