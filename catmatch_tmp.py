import os, dateutil.parser

catdir = os.path.join('out', 'cat', 'sym')

from process import get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, SidTime

for (path, subdirs, files) in os.walk(catdir):
    print path
    subdirs.sort()
    files.sort()

    for fname in files:
        dt = dateutil.parser.parse(fname.split('.')[0])
        sidtime = SidTime.objects.filter(time__lt=get_sidereal_time(dt)).order_by('-time')[0]
        image = Image.objects.get(datetime=dt)
        image.sidtime = sidtime
        image.save()
        
