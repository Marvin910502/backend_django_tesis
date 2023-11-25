from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status


from netCDF4 import Dataset
from wrf import getvar, latlon_coords
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np


class PruebaError(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        data = self.request.data
        urls = data.get('urls')
        diagnostic = data.get('diagnostic')
        index = data.get('index')
        units = data.get('units')

        wrfout = [Dataset(url) for url in urls]
        diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)

        maximum = round(diag.data.max(), 8)
        minimum = round(diag.data.min(), 8)
        extra_max = 0.2 * maximum / 100
        intervals = round((maximum - minimum) / 10, 8)
        lats, lons = latlon_coords(diag)

        figure = plt.figure()
        ax = figure.add_subplot(111)
        lvl = np.around(np.arange(minimum, maximum + extra_max, intervals), 4)
        contourf = ax.contourf(lons, lats, diag, levels=lvl, cmap='coolwarm')
        plt.close('all')

        geojson = geojsoncontour.contourf_to_geojson(
            contourf=contourf,
            min_angle_deg=3.0,
            ndigits=3,
            stroke_width=1,
            fill_opacity=0.5,
        )

        return Response(status=status.HTTP_200_OK)
