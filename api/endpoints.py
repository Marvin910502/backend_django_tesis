# Python libraries
import json
import os
from builtins import max, min

# Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

# Django
from django.contrib.auth.models import User
from api.models import WRFoutFileList
from workers.models import Worker, Map

# WRF libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
from wrf import getvar, latlon_coords

# Selectors
from api.type_data import MAPS_RESULT_2D, MAPS_DIAGNOSTICS_2D_LABEL, MAPS_UNITS_LABEL


# Auth endpoints -------------------------------------------------------------------------------------------------------


class GetUserData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data

            user = User.objects.filter(username=data.get('username')).first()
            worker = user.worker_set.first()
            response = {
                'name': worker.name,
                'last_names': worker.last_names,
                'department': worker.department,
                'isAdmin': worker.isAdmin,
                'isGuess': worker.isGuess,
                'isManager': worker.isManager
            }

            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=500)


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data

            username = data['username']
            password = data['password']
            name = data['name']
            last_names = data['last_names']
            department = data['department']

            if User.objects.filter(username=username).first():
                return Response({'error': 'User already exists'})
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=username
                )
                Worker.objects.create(
                    user=user,
                    name=name,
                    last_names=last_names,
                    department=department,
                    isGuess=True
                )

                return Response({"success": "User create successfully"}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WRF diagnostic endpoints ---------------------------------------------------------------------------------------------


class TwoDimensionsVariablesMaps(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            urls = data.get('url')
            diagnostic = MAPS_RESULT_2D[data.get('diagnostic')]
            index = data.get('index')
            units = data.get('units')
            polygons = data.get('polygons')

            wrfout = [Dataset(url) for url in urls]
            if 'default' in units:
                diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
            else:
                diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)
            maximum = round(diag.data.max(), 8)
            minimum = round(diag.data.min(), 8)
            extra_max = 0.2*maximum/100
            intervals = round((maximum - minimum) / polygons, 8)
            lats, lons = latlon_coords(diag)

            figure = plt.figure()
            ax = figure.add_subplot(111)
            lvl = np.around(np.arange(minimum, maximum + extra_max, intervals), 4)
            contourf = ax.contourf(lons, lats, diag, levels=lvl, cmap=plt.cm.jet)

            geojson = geojsoncontour.contourf_to_geojson(
                contourf=contourf,
                min_angle_deg=3.0,
                ndigits=3,
                stroke_width=1,
                fill_opacity=0.5,
            )

            status_code = 200
            response = {
                'geojson': geojson,
                'success': 'The data went process',
            }

            return Response(response, status=status_code)
        except:
            return Response({'error': 'Something went wrong'}, status=500)


# Files manager endpoints ----------------------------------------------------------------------------------------------


class GetListFiles(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        WRFoutFileList.refresh_list_of_files()
        list_file = []
        for file in WRFoutFileList.objects.all().order_by('name'):
            list_file.append(
                {
                    'name': file.name,
                    'path': file.path,
                    'size': file.size,
                }
            )

        return Response(list_file, status=200)


# Worker map data endpoints --------------------------------------------------------------------------------------------


class SaveMapData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            worker = Worker.objects.filter(user__email=data['user']).first()
            geojson = data.get('geojson')
            diagnostic = data.get('diagnostic')
            units = data.get('units')
            polygons = data.get('polygons')
            file_name = data.get('file_name')

            maps = Map.objects.filter(worker=worker)
            if not maps.filter(file_name=file_name).first():
                Map.objects.create(
                    worker=worker,
                    geojson=geojson,
                    diagnostic=diagnostic,
                    unit=units,
                    polygons=polygons,
                    file_name=file_name
                )
                return Response({'success': 'A map data was save with success'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Something went wrong'}, status=status.HTTP_208_ALREADY_REPORTED)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetListMapData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            worker = Worker.objects.filter(user__email=data.get('username')).first()
            maps = Map.objects.filter(worker=worker).order_by(data.get('order_element'))
            response = []
            for map in maps:
                response.append({
                    'geojson': map.geojson,
                    'diagnostic_label': MAPS_DIAGNOSTICS_2D_LABEL[map.diagnostic],
                    'units_label': MAPS_UNITS_LABEL[map.unit],
                    'polygons': map.polygons,
                    'file_name': map.file_name,
                    'diagnostic': map.diagnostic,
                    'units': map.unit
                })

            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteMapData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            worker = Worker.objects.filter(user__email=data.get('username')).first()
            map = Map.objects.filter(file_name=data.get('file_name'), worker=worker).first()
            map.delete()
            return Response({'success': 'Map data deleted'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

