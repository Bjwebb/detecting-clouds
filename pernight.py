# -*- coding: utf-8 -*-
from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from numpy import mean, std, median, arange

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--exclude-moon', '-e', action='store_true')
parser.add_argument('--table', '-t', action='store_true')
parser.add_argument('--prop', '-p', action='store_true')
args = parser.parse_args()

from collections import defaultdict
nights = defaultdict(list)

#boundaries = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 1.2]
if args.prop:
    #boundaries = [0,0.125,0.25+0.125,0.5+0.125,0.75+0.125,1.0]
    boundaries = [0,0.000001,0.25+0.125,0.5+0.125,1.0-0.000001,1.0]
elif args.table:
    boundaries = [0,0.3,0.6,1.2]
else:
    boundaries = [ x*3 for x in [0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4] ]
#boundaries = [ 1.2*0.5**x for x in range(10,-1,-1) ] 
#boundaries = arange(0,1.2,0.1)
boxes = defaultdict(lambda: defaultdict(list))
boxes['small'] = []
boxes['included'] = []

for line in open('out/perimage-200'+('-hidemoon' if args.exclude_moon else '')+'-data', 'r'):
    # Warning, these indices are 1 smaller than those used by gnuplot
    row = line.split(' ')
    dt = datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':')))
    visibility = float(row[3])
    nights[dt.date()].append(visibility)

    boxes['perimage']['all'].append(dt)
    for boundary in boundaries:
        if visibility < boundary:
            boxes['perimage'][boundary].append(dt)
            break
night_items = nights.items()
night_items.sort()
def prop(visibilties):
    return len([v for v in visibilties if v >= 0.6]) / float(len(visibilties))
night_agg = map(lambda (k,v): (k,sum(v),mean(v),median(v),std(v),max(v),min(v),len(v),prop(v)), night_items)

for date,vis_sum,vis_mean,vis_median,vis_std,vis_max,vis_min,num_images,prop_clear in night_agg:
    # Extremely cloudy 0.01
    # Very cloudy 0.05
    # Rather cloudy 0.1
    # A bit cloudy 0.2
    # Fairly clear 0.3
    if num_images < 10:
        boxes['small'].append(date)
    else:
        boxes['included'].append(date)
        for boundary in reversed(boundaries):
            if vis_min >= boundary:
                boxes['above'][boundary].append(date)
                break
        for boundary in boundaries:
            if vis_max < boundary:
                boxes['below'][boundary].append(date)
                break
        for boundary in boundaries:
            if vis_mean < boundary:
                boxes['mean'][boundary].append(date)
                break
        for boundary in boundaries:
            if vis_median < boundary:
                boxes['median'][boundary].append(date)
                break
        for boundary in boundaries:
            if prop_clear <= boundary and boundary != 0.0:
                boxes['prop_clear'][boundary].append(date)
                break
        #print date,vis_min,vis_mean,vis_max
"""
for k,dates in boxes.items():
    print k
    for date in dates:
        print 'http://localhost:8000/plot/{0}/{1}/{2}/?minpoints=200'.format(date.year, date.month, date.day)
    print
"""

if args.prop:
    for i in range(1, len(boundaries)):
        #if i == 0:
        #    print '"0"',
        #elif i==len(boundaries)-1:
        #    print '"1.0"',
        #elif i==len(boundaries)-2:
        #    print '"'+str(boundaries[i-1])+' < p < '+str(boundaries[i])+'"',
        #else:
        print '"'+str(boundaries[i-1])+' < p ≤ '+str(boundaries[i])+'"',
        print len(boxes['prop_clear'][boundaries[i]]),
        print len(boxes['included'])
elif args.table:
    print int(round(100 * len(boxes['below'][boundaries[1]]) / float(len(boxes['included'])))),
    print '&',
    print int(round(100 * len(boxes['above'][boundaries[2]]) / float(len(boxes['included'])))),
    print '&',
    print int(round(100 * len(boxes['median'][boundaries[1]]) / float(len(boxes['included'])))),
    print '&',
    print int(round(100 * len(boxes['median'][boundaries[3]]) / float(len(boxes['included'])))),
    print
    print
    print int(round(100 * len(boxes['perimage'][boundaries[1]]) / float(len(boxes['perimage']['all'])))),
    print '&',
    print int(round(100 * len(boxes['perimage'][boundaries[3]]) / float(len(boxes['perimage']['all'])))),
    
else:
    for i in range(0, len(boundaries)-1):
        print '"'+str(boundaries[i])+'\\n≤v<\\n'+str(boundaries[i+1])+'"',
        print len(boxes['above'][boundaries[i]]), len(boxes['below'][boundaries[i+1]]), len(boxes['mean'][boundaries[i+1]]), len(boxes['included']), len(boxes['median'][boundaries[i+1]]),
        print len(boxes['perimage'][boundaries[i+1]]), len(boxes['perimage']['all'])

