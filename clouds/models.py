from django.db import models

class SidTime(models.Model):
    time = models.TimeField()

    def __unicode__(self):
        return unicode(self.time)

class Line(models.Model):
    average_flux = models.FloatField(default=0.0)

class Point(models.Model):
    class Meta:
        abstract = True
    x = models.FloatField()
    y = models.FloatField()
    flux = models.FloatField()
    line = models.ForeignKey(Line, null=True)
    idx = models.IntegerField()

class SidPoint(Point):
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
        t = self.sidtime.time
        return 'sid/' + '/'.join([ unicode(x).zfill(2) for x in [ t.hour, t.minute, 'total' ] ]) 

class Image(models.Model):
    datetime = models.DateTimeField()
    sidtime = models.ForeignKey(SidTime, null=True)
    intensity = models.BigIntegerField(null=True)

    def get_url(self):
        return 'sym/' + self.datetime.strftime('%Y/%m/%d/%Y-%m-%dT%H:%M:%S')

class RealPoint(Point):
    sidpoint = models.ForeignKey(SidPoint, null=True)
    image = models.ForeignKey(Image) 

    def get_url(self):
        return self.image.get_url()
        
