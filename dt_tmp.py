from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image
from pytz import timezone, utc

ac = timezone('America/Chicago')

def revert(dt):
    return utc.localize(ac.normalize(utc.localize(dt).astimezone(ac)).replace(tzinfo=None)).replace(tzinfo=None)

for image in Image.objects.order_by('datetime'):
    print image.datetime
    image.datetime = revert(image.datetime)
    image.save()
