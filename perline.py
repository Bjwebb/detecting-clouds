from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from django.db.models import Sum, Max, Count, Avg, StdDev
import sys

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--count-only', '-c', action='store_true')
args = parser.parse_args()

if args.count_only:
    lines = Line.objects.all()
else:
    lines = Line.objects.filter(realpoint__active=True).annotate(
        Count('realpoint'),
        Avg('realpoint__flux'),
        StdDev('realpoint__flux', sample=True),
        Max('realpoint__flux')
        )
for line in lines:
    sys.stdout.write('.')
    sys.stdout.flush()
    line.sidpoint_count = line.sidpoint_set.count()
    if args.count_only:
        line.realpoint_count = line.realpoint_set.count()
    else:
        line.realpoint_count = line.realpoint__count
        line.average_flux = line.realpoint__flux__avg or 0.0
        line.stddev_flux = line.realpoint__flux__stddev or 0.0
        line.max_flux = line.realpoint__flux__max or 0.0
    line.save()

# python perline.py  288.42s user 13.84s system 65% cpu 7:43.99 total
