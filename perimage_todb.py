from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 

hidemoon = open('out/sum200-hidemoondata', 'w')
for line in open('out/sum200data', 'r'):
    # Warning, these indices are 1 smaller than those used by gnuplot
    row = line.split(' ')
    image = Image.objects.get(datetime=datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':'))))
    image.visibility = float(row[2])
    if not image.moon:
        hidemoon.write(line) 
    image.save()
    print image
