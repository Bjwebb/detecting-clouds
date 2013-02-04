import numpy, pandas
import os, datetime, math
import dateutil.parser

catdir = os.path.join('out', 'cat', 'sym')

from process import join, get_subdir, path_split, get_sidereal_time

from django.core.management import setup_environ
import clouds.settings
setup_environ(clouds.settings)
from clouds.models import Image, RealPoint, SidPoint, Line, SidTime 

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
            continue

        # Exclude object larger than 10 pixels
        df = df[ (df[7]-df[5]) < 10 ]
        df = df[ (df[8]-df[6]) < 10 ]

        points = pandas.DataFrame({ 'x': df[9], 'y': df[10], 'f': df[3] })

        sidpoints = SidPoint.objects.filter(sidtime=sidtime).all()
        taken_sidpoint_ids = {}
        realpoints = []
        for i, point in points.iterrows():
            """
            distances = [ (pow(sp.x-point['x'],2)+pow(sp.y-point['y'],2), sp) for sp in sidpoints ]
            d = min(distances)
            """
            sidpoint = sidpoints.extra(select={
                #'d':'(x-{0})*(x-{0}) + (y-{1})*(y-{1})'.format(
                'd':'pow(x-{0}, 2) + pow(y-{1}, 2)'.format(
                    point['x'],point['y'])}).order_by('d')[0]
            if sidpoint.d < 3**2:
                use_sidpoint = True
                if sidpoint.pk in taken_sidpoint_ids:
                    other_realpoint = taken_sidpoint_ids[sidpoint.pk]
                    distance1 = (other_realpoint.x - sidpoint.x)**2 + (other_realpoint.y - sidpoint.y)**2
                    if sidpoint.d < distance1:
                        other_realpoint.sidpoint = None
                    else:
                        use_sidpoint = False
            else:
                use_sidpoint = False

            realpoint = RealPoint(x=point['x'], y=point['y'],
                flux=point['f'],
                idx=i, image=image) 
            if use_sidpoint:
                realpoint.sidpoint = sidpoint
                realpoint.line = sidpoint.line
                taken_sidpoint_ids[sidpoint.pk] = realpoint 
            realpoints.append(realpoint)
            
        RealPoint.objects.bulk_create(realpoints)
