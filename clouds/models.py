from django.db import models

class SidTime(models.Model):
    time = models.TimeField()

    def __unicode__(self):
        return unicode(self.time)

class Line(models.Model):
    pass

# Mayble should distinguish sidpoints from real points
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

class Image(models.Model):
    datetime = models.DateTimeField()

class RealPoint(Point):
    sidpoint = models.ForeignKey(SidPoint, null=True)
    image = models.ForeignKey(Image) 
