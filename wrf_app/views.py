import json
from django.shortcuts import render
# from wrf_app.wrf_funtions import plotting_a_two_dimensional_field
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt

import numpy as np
# from cartopy import crs
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
from wrf import (getvar, interplevel, vertcross,
                 CoordPair, ALL_TIMES, to_np,
                 get_cartopy, latlon_coords,
                 cartopy_xlim, cartopy_ylim)
from backend_django_tesis.settings import BASE_DIR


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def api_mapping(request):
    success = False
    status_code = False

    if request.method == 'POST':
        request_boby = json.loads(request.body)
        if request_boby.get('map_data') == 'lat':
            wrfin = Dataset(f'/home/marvin/PycharmProject/projects/wrf_python_tutorial/wrf_tutorial_data/wrfout_d01_2005-08-28_00_00_00')
            slp = getvar(wrfin, 'slp', timeidx=0)
            lats, lons = latlon_coords(slp)

            figure = plt.figure()
            ax = figure.add_subplot(111)
            lvl = np.arange(980, 1030, 5.5)
            max = lvl.max()
            invert_lvl = lvl[::-1]
            contourf = ax.contourf(lons, lats, slp, cmap=plt.cm.jet)

            geojson = geojsoncontour.contourf_to_geojson(
                contourf=contourf,
                min_angle_deg=3.0,
                ndigits=3,
                stroke_width=2,
                fill_opacity=0.5
            )



            print()
            # lat = np.array(lats)
            # lon = np.array(lons)
            # slp = np.array(slp)
            status_code = 200
            response = {
                'geojson': geojson,
                'success': True,
                'lvl': lvl,
                'max': max,
                'invert_lvl': invert_lvl,
            }

            return Response(response, status=status_code)


def mapping(request):
    return render(request, 'mapping.html')
