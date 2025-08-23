from django.db import models
from rest_framework.exceptions import ValidationError
from workers.models import Worker
from api.models import WRFoutFile

# WRF processing libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
import pandas as pd
from wrf import getvar, latlon_coords
import json


# Create your models here.

def validate_type(value):
    valid_values = [choice[0] for choice in Palette.TYPE_CHOICES]
    if value not in valid_values:
        raise ValidationError(f'{value} no es un valor válido.')

class Palette(models.Model):
    TYPE_CHOICES = [
        ('map', 'Map'),
        ('3d_graphic', '3D Graphic'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, validators=[validate_type])

class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50, unique=True)

class DiagnosticType(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    unit_ids = models.ManyToManyField('Unit', related_name='diagnostic_type_ids')

class Diagnostic(models.Model):
    worker_id = models.ForeignKey(Worker, on_delete=models.CASCADE, null=False, blank=False)
    diagnostic_type_id = models.ForeignKey(DiagnosticType, on_delete=models.CASCADE, null=False, blank=False)
    reference = models.CharField(max_length=200, null=False, blank=False)
    geojson = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
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

    @staticmethod
    def process_wrf_file(**kwargs):
        urls = WRFoutFile.objects.filter(id__in=kwargs.get('url_ids')).values_list('path_file', flat=True)
        diagnostic = DiagnosticType.objects.filter(id=kwargs.get('diagnostic').get('id')).first().value
        map_palette = kwargs.get('map_palette').get('name')
        index = kwargs.get('index')
        units = Unit.objects.filter(id=kwargs.get('units').get('id')).first().symbol
        polygons = kwargs.get('polygons')

        try:
            wrfout = [Dataset(url) for url in urls]
        except Exception as error:
            print(error)

        max_index = 0
        for file in wrfout:
            max_index = max_index + file.dimensions['Time'].size

        diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)
        maximum = round(diag.data.max(), 8)
        minimum = round(diag.data.min(), 8)
        diagnostic_dict = diag.to_dict()

        diagnostic_array = diagnostic_dict['data']
        longitudes = diagnostic_dict['coords']['XLONG']['data']
        min_long = longitudes[0][0]
        max_long = longitudes[0][-1]
        latitudes = diagnostic_dict['coords']['XLAT']['data']
        min_lat = latitudes[0][0]
        max_lat = latitudes[-1][0]


        extra_max = 0.2 * maximum / 100
        intervals = round((maximum - minimum) / polygons, 8)
        lats, lons = latlon_coords(diag)

        figure = plt.figure()
        ax = figure.add_subplot(111)
        plt.close('all')
        lvl = np.around(np.arange(minimum, maximum + extra_max, intervals), 4)
        contourf = ax.contourf(lons, lats, diag, levels=lvl, cmap=map_palette)

        geojson = geojsoncontour.contourf_to_geojson(
            contourf=contourf,
            min_angle_deg=3.0,
            ndigits=3,
            stroke_width=1,
            fill_opacity=0.5,
        )

        data_time = diag.Time.values
        response = {
            'geojsonString': geojson,
            'max_index': max_index,
            'date_time': pd.to_datetime(data_time),
            'lat': round(diag.projection.moad_cen_lat, 0),
            'long': round(diag.projection.stand_lon, 0),
            'data': json.dumps(diagnostic_array),
            'lat3d': json.dumps(latitudes),
            'long3d': json.dumps(longitudes),
            'min_long': min_long,
            'max_long': max_long,
            'min_lat': min_lat,
            'max_lat': max_lat,
        }

        return response
