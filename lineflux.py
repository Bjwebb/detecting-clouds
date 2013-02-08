from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 

for line in Line.objects.annotate(Count('realpoint')).filter(
        realpoint__count__gt=20).annotate(Avg('realpoint__flux')):
    line.average_flux = line.realpoint__flux__avg
    line.save()
