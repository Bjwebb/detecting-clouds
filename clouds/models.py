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

class Line(models.Model):
    average_flux = models.FloatField(default=0.0)
    max_flux = models.FloatField(default=0.0)
    stddev_flux = models.FloatField(default=0.0)
    realpoint_count = models.IntegerField(default=0)
    sidpoint_count = models.IntegerField(default=0)

class Point(models.Model):
    class Meta:
        abstract = True
    x = models.FloatField()
    y = models.FloatField()
    flux = models.FloatField()
    line = models.ForeignKey(Line, null=True)
    idx = models.IntegerField()

class SidPoint(Point):
    class Meta:
        ordering = ['sidtime__time']

    sidtime =  models.ForeignKey(SidTime)
    prev = models.OneToOneField('self', null=True)

    def __getattr__(self, name):
        if name == 'next':
            try:
                return self.sidpoint
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

    def get_url(self):
        return 'sym/' + self.datetime.strftime('%Y/%m/%d/%Y-%m-%dT%H:%M:%S')

    def get_file(self):
        f = self.datetime.strftime
        return os.path.join('sym/', f('%Y'), f('%m'), f('%d'), f('%Y-%m-%dT%H:%M:%S'))

class RealPoint(Point):
    class Meta:
        ordering = ['image__datetime']

    sidpoint = models.ForeignKey(SidPoint, null=True)
    image = models.ForeignKey(Image) 
    active = models.BooleanField(default=True)

    def get_url(self):
        return self.image.get_url()
        
