from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)

from clouds.models import RealPoint
from django.db.models import F
print RealPoint.objects.filter(active=False).update(active=True)
RealPoint.objects.filter(flux__gt=F('line__average_flux')+F('line__stddev_flux')*2).update(active=False)
from django.db import connection
print connection.queries