from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from django.db.models import Count, Sum, Avg, F
from django.db.models.query import QuerySet

from clouds.models import RealPoint
import PIL.Image, PIL.ImageDraw
import pickle, os
from django.db import connection

minimum_points = 200
generation=1

if os.path.exists('totalimage.pickle'):
    realpoints = pickle.load(open('totalimage.pickle', 'r'))
else:
    kwargs = dict(line__linevalues__generation__pk=2, line__linevalues__realpoint_count__gt=minimum_points)
    """
    realpoints = RealPoint.objects.filter(
    #realpoints = RealPoint.objects.filter(x__gt=0,x__lt=40,y__gt=0,y__lt=90,
    #realpoints = RealPoint.objects.filter(x__gt=190,x__lt=200,y__gt=190,y__lt=200,
        generation=generation, sidpoint__isnull=False, active=True,
        **kwargs).extra(select={
            'ix':'floor(clouds_realpoint.x)',
            'iy':'floor(clouds_realpoint.y)',
    #        'deviation': 'AVG(clouds_realpoint.flux/clouds_linevalues.median_flux)',
        }).values('ix', 'iy').annotate(
            sum=Sum('flux'),
            count=Count('pk'),
            avg=Avg('flux'),
        ).order_by()
    """
    cursor = connection.cursor()
    cursor.execute("""SELECT (floor(clouds_realpoint.y)) AS "iy", (floor(clouds_realpoint.x)) AS "ix", COUNT("clouds_realpoint"."id") AS "count", SUM("clouds_realpoint"."flux") AS "sum", AVG("clouds_realpoint"."flux") AS "avg", AVG(clouds_realpoint.flux/clouds_linevalues.median_flux) AS "deviation"
FROM "clouds_realpoint"
INNER JOIN "clouds_line" ON ("clouds_realpoint"."line_id" = "clouds_line"."id")
INNER JOIN "clouds_linevalues" ON ("clouds_line"."id" = "clouds_linevalues"."line_id")
INNER JOIN "clouds_sidpoint" ON ("clouds_realpoint"."sidpoint_id" = "clouds_sidpoint"."id")
INNER JOIN "clouds_image" ON ("clouds_realpoint"."image_id" = "clouds_image"."id")
WHERE ("clouds_realpoint"."active" = True
    AND "clouds_linevalues"."generation_id" = 3
    AND "clouds_realpoint"."generation_id" = 1
    AND "clouds_linevalues"."realpoint_count" > 200
    AND "clouds_sidpoint"."id" IS NOT NULL
    AND "clouds_image"."moon" = False)
GROUP BY (floor(clouds_realpoint.y)), (floor(clouds_realpoint.x))""")
    realpoints = cursor.fetchall()
    pickle.dump(list(realpoints), open('totalimage.pickle', 'w'))
#print list(realpoints.values('line').distinct())
#print realpoints
print len(realpoints)
#import sys
#sys.exit()

i = {'iy':0, 'ix':1, 'count':2, 'sum':3, 'avg':4, 'deviation':5}

for agg, scale in [('count',1), ('sum',5000.0), ('avg',50.0), ('deviation', 0.01) ]:
    im = PIL.Image.new('RGB', (640,480), (0,0,0))
    draw = PIL.ImageDraw.Draw(im)
    for realpoint in realpoints:
        col = int(realpoint[i[agg]] / scale)
        if col > 255: col = 255
        draw.point((realpoint[i['ix']],realpoint[i['iy']]), fill=(col,col,col))
    im.save('totalimage_{0}.png'.format(agg))
