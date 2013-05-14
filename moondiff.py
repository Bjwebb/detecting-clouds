from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 

hidemoon = open('out/perimage-200-hidemoon-data', 'r')
nomoon = open('out/perimage-200-nomoon-data', 'r')
nomoondict = {}
for line in nomoon:
    # Warning, these indices are 1 smaller than those used by gnuplot
    row = line.split(' ')
    dt = datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':')))
    visibility = float(row[3])
    nomoondict[dt] = visibility
for line in hidemoon:
    row = line.split(' ')
    dt = datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':')))
    visibility = float(row[3])
    try:
        print (visibility - nomoondict[dt])/nomoondict[dt]
    except ZeroDivisionError:
        pass
