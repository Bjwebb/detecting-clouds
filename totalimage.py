from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from django.db.models import Count

from clouds.models import RealPoint
import PIL.Image, PIL.ImageDraw

minimum_points = 20
generation=1

kwargs = dict(line__linevalues__generation__pk=2, line__linevalues__realpoint_count__gt=minimum_points)
realpoints = RealPoint.objects.filter(
#realpoints = RealPoint.objects.filter(x__gt=0,x__lt=40,y__gt=0,y__lt=90,
#realpoints = RealPoint.objects.filter(x__gt=190,x__lt=200,y__gt=190,y__lt=200,
    generation=generation, sidpoint__isnull=False, active=True,
    **kwargs).extra(select={'ix':'floor(clouds_realpoint.x)', 'iy':'floor(clouds_realpoint.y)'}).values('ix', 'iy').annotate(count=Count('pk')).order_by()
#print list(realpoints.values('line').distinct())
#print realpoints.query
#print realpoints
print len(realpoints)
#import sys
#sys.exit()

im = PIL.Image.new('RGB', (640,480), (0,0,0))
draw = PIL.ImageDraw.Draw(im)
for realpoint in realpoints:
    col = realpoint['count']
    if col > 255: col = 255
    draw.point((realpoint['ix'],realpoint['iy']), fill=(col,col,col))
im.save('totalimage.png')
