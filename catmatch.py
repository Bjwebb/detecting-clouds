import numpy, pandas
import os, datetime, math
import dateutil.parser

catdir = os.path.join('out', 'cat', 'sym')

from process import join, get_subdir, path_split, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 

steps = 0
for (path, subdirs, files) in os.walk(catdir):
    print path
    subdirs.sort()
    files.sort()

    subdir = get_subdir(path)

    for fname in files:
        dt = dateutil.parser.parse(fname.split('.')[0])
        sidtime = SidTime.objects.filter(time__lt=get_sidereal_time(dt)).order_by('-time')[0]
        image = Image(datetime=dt)
        image.save()
        print sidtime
        
        try:
            df = pandas.read_csv(os.path.join(path, fname), delim_whitespace=True, comment='#', header=None, skiprows=11)
        except ZeroDivisionError:
            # This is thrown if there are no lines in the file
            pass

        # Exclude object larger than 10 pixels
        df = df[ (df[7]-df[5]) < 10 ]
        df = df[ (df[8]-df[6]) < 10 ]

        points = pandas.DataFrame({ 'x': df[9], 'y': df[10], 'f': df[3] })
        print len(points)


        for i, point in points.iterrows():
            sidpoints = SidPoint.objects.filter(sidtime=sidtime)
            sidpoint = sidpoints.extra(select={
                'd':'(x-{0})*(x-{0}) + (y-{1})*(y-{1})'.format(
                    point['x'],point['y'])}).order_by('d')[0]
            try:
                other_realpoint = sidpoint.realpoint_set.get(image=image)
                distance1 = (other_realpoint.x - sidpoint.x)**2 + (other_realpoint.y - sidpoint.y)**2
                if sidpoint.d < distance1:
                    other_realpoint.sidpoint = None
                    other_realpoint.save()
                else:
                    continue
            except RealPoint.DoesNotExist:
                pass
            realpoint = RealPoint(x=point['x'], y=point['y'],
                flux=point['f'],
                idx=i, image=image) 
            if sidpoint.d < 3**2:
                realpoint.sidpoint = sidpoint
                realpoint.line = sidpoint.line
            realpoint.save()

    steps += 1

    #if steps > 10:
    #    break

