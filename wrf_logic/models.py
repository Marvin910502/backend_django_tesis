from django.db import models
from rest_framework.exceptions import ValidationError

from workers.models import Worker

# Create your models here.

def validate_type(value):
    valid_values = [choice[0] for choice in Palette.TYPE_CHOICES]
    if value not in valid_values:
        raise ValidationError(f'{value} no es un valor válido.')

class Diagnostic(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    geojson = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
    diagnostic = models.CharField(max_length=100)
    map_palet = models.CharField(max_length=100, null=True, blank=True)
    maximum = models.FloatField(null=True, blank=True)
    minimum = models.FloatField(null=True, blank=True)
    date_time = models.DateTimeField(max_length=150, null=True, blank=True)
    unit = models.CharField(max_length=20)
    polygons = models.IntegerField()
    file_name = models.CharField(max_length=100)
    z = models.TextField()
    x = models.TextField()
    y = models.TextField()
    min_x = models.FloatField()
    max_x = models.FloatField()
    min_y = models.FloatField()
    max_y = models.FloatField()

class Palette(models.Model):
    TYPE_CHOICES = [
        ('map', 'Map'),
        ('3d_graphic', '3D Graphic'),
    ]

    label = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, validators=[validate_type])