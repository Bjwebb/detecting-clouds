from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg 
import os, sys

for sidtime in SidTime.objects.annotate(Count('sidpoint')).order_by('time'):
    print sidtime.time, sidtime.sidpoint__count

