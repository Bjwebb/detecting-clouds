from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image

Image.objects.update(moon=True)
Image.objects.filter(intensity__lt=2*10**8).update(moon=False)
