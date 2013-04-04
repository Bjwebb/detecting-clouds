from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import *
from django.db.models import Sum, Max, Count, Avg, StdDev
import sys

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--count-only', '-c', action='store_true')
parser.add_argument('--generation', '-g', type=int, default=1)
args = parser.parse_args()

generation_pk = args.generation

from django.db import connection, transaction
cursor = connection.cursor()
cursor.execute("DELETE FROM clouds_linevalues WHERE generation_id=%s", [generation_pk])
transaction.commit_unless_managed()

if args.count_only:
    lines = Line.objects.all()
else:
    if generation_pk == 1:
        lines_ = Line.objects.all()
    else:
        lines_ = Line.objects.filter(realpoint__active=True)
    lines = lines_.annotate(
        Count('realpoint'),
        Avg('realpoint__flux'),
        StdDev('realpoint__flux', sample=True),
        Max('realpoint__flux')
        )
for line in lines:
    sys.stdout.write('.')
    sys.stdout.flush()
    generation, created = LineValuesGeneration.objects.get_or_create(pk=generation_pk)
    linevalues = LineValues(line=line, generation=generation)
    linevalues.sidpoint_count = line.sidpoint_set.count()
    if args.count_only:
        linevalues.realpoint_count = line.realpoint_set.count()
    else:
        linevalues.realpoint_count = line.realpoint__count
        linevalues.average_flux = line.realpoint__flux__avg or 0.0
        linevalues.stddev_flux = line.realpoint__flux__stddev or 0.0
        linevalues.max_flux = line.realpoint__flux__max or 0.0
    linevalues.save()

# python perline.py  288.42s user 13.84s system 65% cpu 7:43.99 total
