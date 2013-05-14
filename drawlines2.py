import PIL.Image, PIL.ImageDraw
from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import SidPoint, Line, SidTime

im = PIL.Image.new('RGB', (640,480), 'white')
draw = PIL.ImageDraw.Draw(im)
sidpoints = SidTime.objects.get(pk=1).sidpoint_set.filter(line__linevalues__generation_id=2, line__linevalues__sidpoint_count__gt=200).order_by('x')[520:540]

for sidpoint in sidpoints:
    line = sidpoint.line
    prev_point = None
    for point in line.sidpoint_set.select_related('prev').all():
        prev_point = point.prev
        if type(prev_point) == type(None):
            draw.point((point.x, point.y), fill='black')
        else:
            draw.line((prev_point.x, prev_point.y, point.x, point.y), fill='black')

im.save(open('drawlines2.png', 'w'), format='PNG')
