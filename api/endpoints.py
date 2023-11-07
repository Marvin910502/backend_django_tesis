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
from django.contrib.auth import authenticate
from django.utils.text import slugify
from api.models import WRFoutFileList
from workers.models import Worker, Diagnostic
from manager.models import Content
from backend_django_tesis.settings import BASE_DIR

# WRF processing libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
from wrf import getvar, latlon_coords, extract_times


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
            name = data.get('name')
            last_names = data.get('last_names')
            department = data.get('department')

            if User.objects.filter(username=username).first():
                return Response({'error': 'User already exists'}, status=status.HTTP_401_UNAUTHORIZED)
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


class UpdateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data

            old_username = data['old_username']
            username = data['username']
            name = data['name']
            last_names = data['last_names']
            department = data['department']

            user = User.objects.filter(username=old_username).first()
            if user:
                worker = user.worker_set.first()

                user.username = username
                user.email = username
                user.save()

                worker.name = name
                worker.last_names = last_names
                worker.department = department
                worker.save()

                return Response({'success': 'User updated successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'The user not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswd(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data

            username = data['username']
            old_password = data['old_password']
            password = data['new_password']

            if authenticate(username=username, password=old_password):
                user = User.objects.filter(username=username).first()
                user.set_password(password)
                user.save()

                return Response({'success': 'Password changed successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Wrong old password'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WRF diagnostic endpoints ---------------------------------------------------------------------------------------------


class TwoDimensionsVariablesMaps(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            urls = data.get('url')
            diagnostic = MAPS_RESULT_2D.get(data.get('diagnostic'))
            index = data.get('index')
            units = MAPS_UNITS_LABEL.get(data.get('units'))
            polygons = data.get('polygons')

            if not urls:
                return Response({'error': 'No url data'}, status=status.HTTP_400_BAD_REQUEST)
            if not diagnostic:
                return Response({'error': 'No diagnostic data'}, status=status.HTTP_400_BAD_REQUEST)
            if index is None:
                return Response({'error': 'No index data'}, status=status.HTTP_400_BAD_REQUEST)
            if not units:
                return Response({'error': 'No units data'}, status=status.HTTP_400_BAD_REQUEST)
            if polygons is None:
                return Response({'error': 'No polygons data'}, status=status.HTTP_400_BAD_REQUEST)

            wrfout = [Dataset(url) for url in urls]

            max_index = 0
            for file in wrfout:
                max_index = max_index + file.dimensions['Time'].size

            if 'default' in units:
                try:
                    diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
                except:
                    return Response({'error': 'The diagnostic extraction fail'})
            else:
                try:
                    diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)
                except:
                    return Response({'error': 'The diagnostic extraction fail'})

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

            response = {
                'geojson': geojson,
                'max_index': max_index,
                'success': 'The data went process',
            }

            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrossSections(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        data = self.request.data
        urls = data.get('url')
        index = data.get('index')
        diagnostic = MAPS_RESULT_2D.get(data.get('diagnostic'))
        units = MAPS_UNITS_LABEL.get(data.get('units'))

        if not urls:
            return Response({'error': 'No url data'}, status=status.HTTP_400_BAD_REQUEST)
        if not diagnostic:
            return Response({'error': 'No diagnostic data'}, status=status.HTTP_400_BAD_REQUEST)
        if index is None:
            return Response({'error': 'No index data'}, status=status.HTTP_400_BAD_REQUEST)
        if not units:
            return Response({'error': 'No units data'}, status=status.HTTP_400_BAD_REQUEST)

        wrfout = [Dataset(url) for url in urls]
        if 'default' in units:
            diagnostic_data = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
        else:
            diagnostic_data = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)

        diagnostic_dict = diagnostic_data.to_dict()

        diagnostic_array = diagnostic_dict['data']
        longitudes = diagnostic_dict['coords']['XLONG']['data']
        min_long = longitudes[0][0]
        max_long = longitudes[0][-1]
        latitudes = diagnostic_dict['coords']['XLAT']['data']
        min_lat = latitudes[0][0]
        max_lat = latitudes[-1][0]

        response = {
            'data': json.dumps(diagnostic_array),
            'longitudes': json.dumps(longitudes),
            'min_long': min_long,
            'max_long': max_long,
            'latitudes': json.dumps(latitudes),
            'min_lat': min_lat,
            'max_lat': max_lat,
            'success': 'The data went process',
        }

        return Response(response, status=status.HTTP_200_OK)


# Files manager endpoints ----------------------------------------------------------------------------------------------


class GetListFiles(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        WRFoutFileList.refresh_list_of_files()
        data = self.request.data
        list_file = []
        for file in WRFoutFileList.objects.all().order_by(data.get('order')):
            if file.path_file:
                path = file.path_file.path
            else:
                path = file.path_string
            list_file.append(
                {
                    'name': file.name,
                    'path': path,
                    'size': file.size,
                }
            )

        return Response(list_file, status=200)


class SaveFile(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            file = data.get('file')
            wrf_data = WRFoutFileList.objects.create(
                name=file.name.replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
                path_file=file,
                size=round(file.size/1000000, 2)
            )

            try:
                Dataset(wrf_data.path_file.path)
            except:
                os.remove(f"{BASE_DIR}/wrfout_files/{wrf_data.name}")
                wrf_data.delete()
                return Response({'error': 'This type of file is not compatible'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response({'success': 'The was uploaded'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteFile(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            data = self.request.data
            os.remove(f"{BASE_DIR}/wrfout_files/{data.get('file_name')}")
            return Response({'success': 'The file was deleted'})
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            diagnostics = Diagnostic.objects.filter(worker=worker)
            if not diagnostics.filter(file_name=file_name).first():
                Diagnostic.objects.create(
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
            diagnostics = Diagnostic.objects.filter(worker=worker).order_by(data.get('order_element'))
            response = []
            for diagnostic in diagnostics:
                response.append({
                    'geojson': diagnostic.geojson,
                    'diagnostic_label': MAPS_DIAGNOSTICS_2D_LABEL[diagnostic.diagnostic],
                    'units_label': MAPS_UNITS_LABEL[diagnostic.unit],
                    'polygons': diagnostic.polygons,
                    'file_name': diagnostic.file_name,
                    'diagnostic': diagnostic.diagnostic,
                    'units': diagnostic.unit
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
            diagnostic = Diagnostic.objects.filter(file_name=data.get('file_name'), worker=worker).first()
            diagnostic.delete()
            return Response({'success': 'Map data deleted'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Contents endpoint ----------------------------------------------------------------------------------------------------

class GetContent(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            content = Content.objects.first()
            response = {
                'home_content': content.home_content,
                'card_diagnostics': content.card_diagnostics,
                'card_my_diagnostics': content.card_my_diagnostics,
                'help_content': content.help_content
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
