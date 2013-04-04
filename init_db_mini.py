from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)

from clouds.models import Image, SidTime 
import datetime, os
import dateutil.parser
from utils import sidday, timedelta_as_time, get_sidereal_time

limit = datetime.timedelta(minutes=5)

delta = datetime.timedelta(minutes=1)
s = datetime.timedelta(0)
while s < limit:
    sidtime = SidTime(time=timedelta_as_time(s))
    sidtime.save()
    s += delta

symdir = os.path.join('sym')
for (path, subdirs, files) in os.walk('sym'):
    subdirs.sort()
    files.sort()

    for fname in files:
        dt = dateutil.parser.parse(fname.split('.')[0])
        time = get_sidereal_time(dt)
        if time < limit:
            sidtime = SidTime.objects.filter(time__lt=get_sidereal_time(dt)).order_by('-time')[0]
            print sidtime
            image = Image(datetime=dt, sidtime=sidtime)
            image.save()

