from django.db import models
import os, datetime

class SidTime(models.Model):
    time = models.TimeField(unique=True)

    def __unicode__(self):
        return unicode(self.time)
    
    def gnuplot_datetime(self):
        return datetime.datetime.combine(datetime.date(2000,1,1), self.time)

    def get_dir(self):
        t = self.time
        return os.path.join('sid/', os.path.join(*[ unicode(x).zfill(2) for x in [ t.hour, t.minute ] ]))

    def get_url(self):
        t = self.time
        return 'sid/' + '/'.join([ unicode(x).zfill(2) for x in [ t.hour, t.minute, 'total' ] ]) 

    def magic_points(self):
        return self.sidpoint_set.prefetch_related('line__linevalues_set').prefetch_related('sidtime')

class Line(models.Model):
    linevaluegeneration = 3

    def first_sidpoint(self):
        return self.sidpoint_set.get(prev=None)
    def last_sidpoint(self):
        return self.sidpoint_set.get(sidpoint=None)

    def __getattr__(self, name):
        if name in ['average_flux', 'median_flux', 'max_flux', 'stddev_flux', 'realpoint_count', 'sidpoint_count']:
            #try:
                #return getattr(self.linevalues_set.get(generation_id=4), name)
            #except LineValues.DoesNotExist:
                # Do this to make use of prefetch_related:
                for linevalue in self.linevalues_set.all():
                    if linevalue.generation_id == self.linevaluegeneration:
                        return getattr(linevalue, name)
                return
        else:
            return getattr(super(Line, self), name)

class LineValuesGeneration(models.Model):
    pass

class LineValues(models.Model):
    class Meta:
        unique_together = ('line', 'generation')

    line = models.ForeignKey(Line)
    generation = models.ForeignKey(LineValuesGeneration)
    average_flux = models.FloatField(default=0.0)
    median_flux = models.FloatField(default=0.0)
    max_flux = models.FloatField(default=0.0)
    stddev_flux = models.FloatField(default=0.0)
    realpoint_count = models.IntegerField(default=0)
    sidpoint_count = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.pk)

class Point(models.Model):
    class Meta:
        abstract = True
    x = models.FloatField()
    y = models.FloatField()
    x_min = models.FloatField()
    y_min = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    flux = models.FloatField()
    flux_error = models.FloatField()
    line = models.ForeignKey(Line, null=True)
    idx = models.IntegerField()

class SidPoint(Point):
    class Meta:
        ordering = ['sidtime__time']
        unique_together = (('sidtime', 'idx'),)

    sidtime =  models.ForeignKey(SidTime)
    prev = models.OneToOneField('self', null=True)
    step = models.IntegerField(null=True) # Should be null iff prev is

    def __getattr__(self, name):
        if name == 'next':
            try:
                return SidPoint.objects.select_for_update().get(prev=self)
            except SidPoint.DoesNotExist:
                return None
        else:
            return getattr(super(SidPoint, self), name)

    def __unicode__(self):
        return unicode(self.sidtime)

    def get_url(self):
        return self.sidtime.get_url()

class Image(models.Model):
    datetime = models.DateTimeField(unique=True)
    sidtime = models.ForeignKey(SidTime, null=True)
    intensity = models.BigIntegerField(null=True)
    visibility = models.FloatField(null=True)
    moon = models.BooleanField(default=False)

    def get_url(self):
        return 'sym/' + self.datetime.strftime('%Y/%m/%d/%Y-%m-%dT%H:%M:%S')

    def get_file(self):
        f = self.datetime.strftime
        return os.path.join('sym/', f('%Y'), f('%m'), f('%d'), f('%Y-%m-%dT%H:%M:%S'))

    def __unicode__(self):
        return unicode(self.datetime)

    def magic_points(self):
        return self.realpoint_set.prefetch_related('line__linevalues_set').prefetch_related('image')

class RealPointGeneration(models.Model):
    pass

class RealPoint(Point):
    class Meta:
        ordering = ['image__datetime']

    sidpoint = models.ForeignKey(SidPoint, null=True)
    image = models.ForeignKey(Image) 
    active = models.BooleanField(default=True)
    # FIXME This field has inconsistent support
    generation = models.ForeignKey(RealPointGeneration, default=lambda: RealPointGeneration.objects.get_or_create(pk=1)[0].pk)

    def get_url(self):
        return self.image.get_url()
        
