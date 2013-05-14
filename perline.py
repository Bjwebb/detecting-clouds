from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import *
from django.db.models import Sum, Min, Max, Count, Avg, StdDev, F
from django.db import reset_queries
import sys

from django.db.models.sql.aggregates import Aggregate
# class borrowed from https://groups.google.com/d/msg/django-users/vVprMpsAnPo/GH8aLo5892MJ
class Median(Aggregate):
    sql_function = 'median'
    def __init__(self, lookup, **extra):
        self.lookup = lookup
        self.extra = extra

    def _default_alias(self):
        return '%s__%s' % (self.lookup, self.__class__.__name__.lower())
    default_alias = property(_default_alias)

    def add_to_query(self, query, alias, col, source, is_summary):
        super(Median, self).__init__(col, source, is_summary, **self.extra)
        query.aggregate_select[alias] = self

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--count-only', '-c', action='store_true')
parser.add_argument('--filter', '-f', action='store_true')
parser.add_argument('--line-filter', '-a', action='store_true')
parser.add_argument('--generation', '-g', type=int, default=1)
parser.add_argument('--prev_generation', '-p', type=int, default=0)
parser.add_argument('--reset', '-r', action='store_true')
parser.add_argument('--negative', '-n', action='store_true')
parser.add_argument('--line', '-l', type=int, default=0)
parser.add_argument('--exclude-moon', '-e', action='store_true')
args = parser.parse_args()
generation_pk = args.generation

def add_values_for_lines(lines):
    if not args.count_only:
        if args.exclude_moon:
            lines = lines.filter(realpoint__active=True,
                                 realpoint__image__moon=False)
        else:
            lines = lines.filter(realpoint__active=True)
        lines = lines.annotate(
            Count('realpoint'),
            Avg('realpoint__flux'),
            Median('realpoint__flux'),
            StdDev('realpoint__flux', sample=True),
            Max('realpoint__flux')
            )
    if generation_pk > 1:
        if args.prev_generation > 0:
            lines = lines.filter(linevalues__generation_id=args.prev_generation)
        else:
            lines = lines.filter(linevalues__generation_id=generation_pk-1)

    linevaluess = []
    generation, created = LineValuesGeneration.objects.get_or_create(pk=generation_pk)
    for line in lines:
        sys.stdout.write('.')
        sys.stdout.flush()
        linevalues = LineValues(line=line, generation=generation)
        linevalues.sidpoint_count = line.sidpoint_set.count()
        if args.count_only:
            linevalues.realpoint_count = line.realpoint_set.count()
        else:
            linevalues.realpoint_count = line.realpoint__count
            linevalues.average_flux = line.realpoint__flux__avg or 0.0
            linevalues.median_flux = line.realpoint__flux__median or 0.0
            linevalues.stddev_flux = line.realpoint__flux__stddev or 0.0
            linevalues.max_flux = line.realpoint__flux__max or 0.0
        linevaluess.append(linevalues)
    LineValues.objects.bulk_create(linevaluess)
    reset_queries()


def add_values_worker(bounds):
    minpk, maxpk = bounds
    lines = Line.objects.filter(pk__gte=minpk, pk__lt=maxpk)
    try:
        add_values_for_lines(lines)
    except KeyboardInterrupt:
        raise ExitError

def filter_worker(bounds):
    try:
        minpk, maxpk = bounds
        realpoints = RealPoint.objects.filter(line__pk__gte=minpk, line__pk__lt=maxpk)
        if args.reset:
            print realpoints.filter(active=False).update(active=True)
        elif args.negative:
            print realpoints.filter(flux__lt=0
                ).update(active=False)
        else:
            print realpoints.filter(line__linevalues__generation__pk=generation_pk
                ).filter(flux__gt=F('line__linevalues__median_flux')*3
                ).update(active=False)
        reset_queries()
    except KeyboardInterrupt:
        raise ExitError

def filter_line_worker(bounds):
    try:
        minpk, maxpk = bounds
        linevaluess = []
        generation, created = LineValuesGeneration.objects.get_or_create(pk=generation_pk)
        lines = Line.objects.filter(pk__gte=minpk, pk__lt=maxpk,
                realpoint__active=True).annotate(
                    Min('realpoint__x'), Max('realpoint__x'),
                    Min('realpoint__y'), Max('realpoint__y'),
                )
        if generation_pk > 1:
            lines = lines.filter(linevalues__generation_id=generation_pk-1)
        for line in lines:
            diagonal_sq = (line.realpoint__x__max - line.realpoint__x__min)**2 + (line.realpoint__y__max - line.realpoint__y__min)**2
            if (diagonal_sq > 1600 or
                    (line.realpoint__x__max < 300 and line.realpoint__x__min > 240)
                    and line.realpoint__y__max < 460 and line.realpoint__y__min > 400):
                    # ( avoid missing long loops very close to the axis)
                    # without 9943, with 12068 
                linevalues = line.linevalues_set.get(generation__pk=generation_pk-1)
                linevalues.pk = None
                linevalues.generation = generation
                linevaluess.append(linevalues)
        LineValues.objects.bulk_create(linevaluess)
        reset_queries()
    except KeyboardInterrupt:
        raise ExitError

if __name__ == '__main__':
    from multiprocessing import Pool
    pool = Pool(20)
    
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

        if args.line_filter:
            pool.map(filter_line_worker, chunks)
        else:
            pool.map(add_values_worker, chunks)

