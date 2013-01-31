from PIL import Image, ImageDraw
from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime 
from process import join

beginning = SidTime.objects.get(pk=1)

im = Image.new('RGB', (640,480), 'white')
draw = ImageDraw.Draw(im)

prev_points = None
sidtimes = SidTime.objects.all()
for sidtime in sidtimes:
    print sidtime
    points = SidPoint.objects.filter(sidtime=sidtime, line__sidpoint__sidtime=beginning)
    for point in points:
        try:
            prev_point = point.prev
            if type(prev_point) == type(None):
                draw.line((point.x, point.y, point.x, point.y), fill='black')
            else:
                draw.line((prev_point.x, prev_point.y, point.x, point.y), fill='black')
        except AttributeError:
            draw.line((point.x, point.y, point.x, point.y), fill='black')
    im.save(join('out','postdb','drawlines',unicode(sidtime.time)+'.png'))
    prev_points = points
