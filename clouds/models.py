from django.db import models

class SidTime(models.Model):
    time = models.TimeField()

class Line(models.Model):
    pass

# Mayble should distinguish sidpoints from real points
class Point(models.Model):
    class Meta:
        abstract = True
    x = models.FloatField()
    y = models.FloatField()
    flux = models.FloatField()
    line = models.ForeignKey(Line)
    idx = models.IntegerField()

class SidPoint(Point):
    sidtime =  models.ForeignKey(SidTime)

class RealPoint(Point):
    sidpoint =  models.ForeignKey(SidTime)
    datetime = models.DateTimeField()
