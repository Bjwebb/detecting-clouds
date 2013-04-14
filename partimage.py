from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)

from clouds.models import Image
import math
import PIL.Image, PIL.ImageDraw

minimum_points = 20
generation=1

import sys
image = Image.objects.get(pk=sys.argv[1])
kwargs = dict(line__linevalues__generation__pk=4, line__linevalues__realpoint_count__gt=minimum_points)
realpoints = image.realpoint_set.filter(generation=generation, sidpoint__isnull=False,
    active=True, **kwargs)

im = PIL.Image.new('RGB', (640,480), 'white')
draw = PIL.ImageDraw.Draw(im)
def coords(r):
    return (int(realpoint.x-r), int(realpoint.y-r), int(realpoint.x+r), int(realpoint.y+r))
ratios = []
for realpoint in realpoints:
    draw.ellipse(coords(math.log(realpoint.line.max_flux)), fill='black')
    ratio = realpoint.flux/realpoint.line.max_flux
    draw.pieslice(coords(math.log(realpoint.line.max_flux)), 0,int(360*ratio), fill='blue')
    ratios.append(ratio)
im.save('partimage.png')
print sum(ratios)/len(ratios)
