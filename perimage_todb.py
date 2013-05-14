from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
import datetime
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 

hidemoon = open('out/perimage-200-hidemoon-data', 'w')
for line in open('out/perimage-200-data', 'r'):
    # Warning, these indices are 1 smaller than those used by gnuplot
    row = line.split(' ')
    image = Image.objects.get(datetime=datetime.datetime(*map(int ,row[0].split('-') + row[1].split(':'))))
    image.visibility = float(row[3])
    if not image.moon:
        hidemoon.write(line) 
    image.save()
    print image
