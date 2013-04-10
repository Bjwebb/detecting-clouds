from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import *
from django.db.models import Sum, Max, Count, Avg, StdDev, F
import sys

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--count-only', '-c', action='store_true')
parser.add_argument('--filter', '-f', action='store_true')
parser.add_argument('--generation', '-g', type=int, default=1)
parser.add_argument('--reset', '-r', action='store_true')
parser.add_argument('--negative', '-n', action='store_true')
parser.add_argument('--line', '-l', type=int, default=0)
args = parser.parse_args()
generation_pk = args.generation

def add_values_for_lines(bare_lines):
    if args.count_only:
        lines = bare_lines
    else:
        lines_ = bare_lines.filter(realpoint__active=True)
        lines = lines_.annotate(
            Count('realpoint'),
            Avg('realpoint__flux'),
            StdDev('realpoint__flux', sample=True),
            Max('realpoint__flux')
            )
    linevaluess = []
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
        linevaluess.append(linevalues)
    LineValues.objects.bulk_create(linevaluess)


def add_values_worker(bounds):
    minpk, maxpk = bounds
    lines = Line.objects.filter(pk__gte=minpk, pk__lt=maxpk)
    try:
        add_values_for_lines(lines)
    except KeyboardInterrupt:
        raise ExitError

def filter_worker(bounds):
    minpk, maxpk = bounds
    realpoints = RealPoint.objects.filter(line__pk__gte=minpk, line__pk__lt=maxpk)
    if args.reset:
        print realpoints.filter(active=False).update(active=True)
    elif args.negative:
        print realpoints.filter(flux__lt=0
            ).update(active=False)
    else:
        print realpoints.filter(line__linevalues__generation__pk=generation_pk
            ).filter(flux__gt=F('line__linevalues__average_flux')*2
            ).update(active=False)

if __name__ == '__main__':
    from multiprocessing import Pool
    pool = Pool(4)

    chunk_size = 1000
    chunks = [ (x,x+chunk_size) for x in range(0,
                                Line.objects.order_by('-pk')[0].pk, chunk_size)]
    if args.line:
        chunks = [ (args.line,args.line+1) ]
    if args.filter:
        pool.map(filter_worker, chunks)
    else:
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute("DELETE FROM clouds_linevalues WHERE generation_id=%s", [generation_pk])
        transaction.commit_unless_managed()
        connection.close()

        pool.map(add_values_worker, chunks)

