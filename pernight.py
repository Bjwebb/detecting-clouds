from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 
from numpy import mean, std

import argparse
parser = argparse.ArgumentParser(description='Perform some calculations to each line, and add them to the database.')
parser.add_argument('--exclude-moon', '-e', action='store_true')
args = parser.parse_args()

from collections import defaultdict
nights = defaultdict(list)
for line in open('out/sum200'+('-hidemoon' if args.exclude_moon else '')+'data', 'r'):
    # Warning, these indices are 1 smaller than those used by gnuplot
    row = line.split(' ')
    dt = datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':')))
    intensity = float(row[2])
    nights[dt.date()].append(intensity)
night_items = nights.items()
night_items.sort()
night_agg = map(lambda (k,v): (k,sum(v),mean(v),std(v),max(v),min(v),len(v)), night_items)

boxes = defaultdict(lambda: defaultdict(list))
boxes['small'] = []
boxes['included'] = []
boundaries = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 1.0]
for date,vis_sum,vis_mean,vis_std,vis_max,vis_min,num_images in night_agg:
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
            if vis_min > boundary:
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
        #print date,vis_min,vis_mean,vis_max
"""
for k,dates in boxes.items():
    print k
    for date in dates:
        print 'http://localhost:8000/plot/{0}/{1}/{2}/?minpoints=200'.format(date.year, date.month, date.day)
    print
"""

for i in range(0, len(boundaries)-1):
    print '"'+str(boundaries[i])+' - '+str(boundaries[i+1])+'"', len(boxes['above'][boundaries[i]]), len(boxes['below'][boundaries[i+1]]), len(boxes['mean'][boundaries[i+1]]), len(boxes['included'])
