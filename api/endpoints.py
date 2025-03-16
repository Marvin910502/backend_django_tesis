# Python libraries
import json
import os
import uuid
from ipware import get_client_ip
import pandas as pd

# Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

# Django
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpResponse
from api.models import WRFoutFile
from workers.models import Worker, Diagnostic
from manager.models import Content, Logs
from backend_django_tesis.settings import BASE_DIR, MEDIA_PROFILES_URL, MEDIA_ICONS_URL, MEDIA_IMAGES_URL

# WRF processing libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
from wrf import getvar, latlon_coords


# Selectors
from api.type_data import MAPS_RESULT_2D, MAPS_DIAGNOSTICS_2D_LABEL, MAPS_UNITS_LABEL, MAPS_UNITS_TAGS, DEFAULT_UNIT_DIAGNOSTICS, DIAG_DEFAULTS_UNITS


# Auth endpoints -------------------------------------------------------------------------------------------------------

def get_user_ip(request):
    ip, is_routable = get_client_ip(request)
    return ip


def get_serialized_meta_data(request):
    meta_data = {k: str(v) for k, v in request.stream.META.items()}
    serialized_meta_data = json.dumps(meta_data)
    return serialized_meta_data


def create_max_min_data(diagnostic, diagnostics):
    max_list = []
    min_list = []
    dates = []
    current_diagnostics = diagnostics.filter(diagnostic=diagnostic).order_by('date_time')

    for diag in current_diagnostics:
        max_list.append(diag.maximum)
        min_list.append(diag.minimum)
        dates.append(diag.date_time)

    max_min_data = {
        'diag_label': MAPS_DIAGNOSTICS_2D_LABEL[diagnostic],
        'max_list': max_list,
        'min_list': min_list,
        'dates': dates,
        'unit': DIAG_DEFAULTS_UNITS[diagnostic]
    }

    return max_min_data


class GetUserData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            user = User.objects.filter(username=data.get('username')).first()
            worker = user.worker_set.first()
            response = {
                'name': worker.name,
                'last_names': worker.last_names,
                'username': data.get('username'),
                'department': worker.department,
                'isAdmin': worker.isAdmin,
                'isGuess': worker.isGuess,
                'isManager': worker.isManager,
                'profile_image': worker.image_name
            }

            Logs.objects.create(
                action='get_user_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success"
            )
            return Response(response, status=status.HTTP_200_OK)
        except:
            Logs.objects.create(
                action='get_user_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=500)


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            username = data['username']
            password = data['password']
            name = data.get('name')
            last_names = data.get('last_names')
            department = data.get('department')

            if User.objects.filter(username=username).first():
                Logs.objects.create(
                    action='create_user',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='401',
                    ip=get_user_ip(self.request),
                    message="error: User already exists"
                )
                return Response({'error': 'User already exists'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=username
                )
                Worker.objects.create(
                    user=user,
                    name=name if name else '',
                    last_names=last_names if last_names else '',
                    department=department if department else 'Visitante',
                    isGuess=True
                )

                Logs.objects.create(
                    action='create_user',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='201',
                    ip=get_user_ip(self.request),
                    message="success: User create successfully"
                )
                return Response({"success": "User create successfully"}, status=status.HTTP_201_CREATED)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='create_user',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadProfileImage(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            user = User.objects.filter(username=data.get('username')).first()
            worker = Worker.objects.filter(user=user).first()
            file = data.get('file')
            file.name = uuid.uuid4().__str__()

            try:
                os.remove(f"{MEDIA_PROFILES_URL}/{worker.image_name}")
            except Exception as error:
                print(error)
                worker.image_name = ''

            worker.profile_image = file
            worker.image_name = file.name
            worker.save()

            Logs.objects.create(
                action='update_user_avatar',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='201',
                ip=get_user_ip(self.request),
                message="success: Profile image updated"
            )
            return Response({"success": "Profile image updated", "profile_image": worker.image_name}, status=status.HTTP_201_CREATED)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='update_user_avatar',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetProfileImage(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, filename):
        try:
            image_path = os.path.join(MEDIA_PROFILES_URL, filename)
            try:
                with open(image_path, 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/jpg')
            except:
                with open(f'{MEDIA_PROFILES_URL}/default.png', 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/svg')
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
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

                Logs.objects.create(
                    action='update_user',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='201',
                    ip=get_user_ip(self.request),
                    message="success: User updated successfully"
                )
                return Response({'success': 'User updated successfully'}, status=status.HTTP_201_CREATED)
            else:
                Logs.objects.create(
                    action='update_user',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='401',
                    ip=get_user_ip(self.request),
                    message="error: The user not exist"
                )
                return Response({'error': 'The user not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            Logs.objects.create(
                action='update_user',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswd(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            username = data['username']
            old_password = data['old_password']
            password = data['new_password']

            if authenticate(username=username, password=old_password):
                user = User.objects.filter(username=username).first()
                user.set_password(password)
                user.save()

                Logs.objects.create(
                    action='change_password',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='201',
                    ip=get_user_ip(self.request),
                    message="success: Password changed successfully"
                )
                return Response({'success': 'Password changed successfully'}, status=status.HTTP_201_CREATED)
            else:
                Logs.objects.create(
                    action='change_password',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='401',
                    ip=get_user_ip(self.request),
                    message="error: Wrong old password"
                )
                return Response({'error': 'Wrong old password'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='change_password',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# WRF diagnostic endpoints ---------------------------------------------------------------------------------------------


class TwoDimensionsVariablesMaps(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            urls = data.get('url')
            diagnostic = MAPS_RESULT_2D.get(data.get('diagnostic'))
            map_palet = data.get('map_palet')
            index = data.get('index')
            units = MAPS_UNITS_LABEL.get(data.get('units'))
            polygons = data.get('polygons')

            if not urls:
                Logs.objects.create(
                    action='2d_maps_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No url data"
                )
                return Response({'error': 'No url data'}, status=status.HTTP_400_BAD_REQUEST)
            if not diagnostic:
                Logs.objects.create(
                    action='2d_maps_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No diagnostic data"
                )
                return Response({'error': 'No diagnostic data'}, status=status.HTTP_400_BAD_REQUEST)
            if index is None:
                Logs.objects.create(
                    action='2d_maps_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No index data"
                )
                return Response({'error': 'No index data'}, status=status.HTTP_400_BAD_REQUEST)
            if not units:
                Logs.objects.create(
                    action='2d_maps_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No units data"
                )
                return Response({'error': 'No units data'}, status=status.HTTP_400_BAD_REQUEST)
            if polygons is None:
                Logs.objects.create(
                    action='2d_maps_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No polygons data"
                )
                return Response({'error': 'No polygons data'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                wrfout = [Dataset(url) for url in urls]
            except Exception as error:
                print(error)

            max_index = 0
            for file in wrfout:
                max_index = max_index + file.dimensions['Time'].size

            maximum = None
            minimum = None

            if data.get('diagnostic') in DEFAULT_UNIT_DIAGNOSTICS:
                try:
                    diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
                    maximum_default = round(diag.data.max(), 8)
                    minimum_default = round(diag.data.min(), 8)
                    maximum = round(diag.data.max(), 8)
                    minimum = round(diag.data.min(), 8)
                except:
                    Logs.objects.create(
                        action='2d_maps_data',
                        username=data.get('username'),
                        metadata=get_serialized_meta_data(self.request),
                        status_code='500',
                        ip=get_user_ip(self.request),
                        message="error: The diagnostic extraction fail"
                    )
                    return Response({'error': 'The diagnostic extraction fail'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                try:
                    diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
                    maximum_default = round(diag.data.max(), 8)
                    minimum_default = round(diag.data.min(), 8)
                    diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)
                    maximum = round(diag.data.max(), 8)
                    minimum = round(diag.data.min(), 8)
                except:
                    Logs.objects.create(
                        action='2d_maps_data',
                        username=data.get('username'),
                        metadata=get_serialized_meta_data(self.request),
                        status_code='500',
                        ip=get_user_ip(self.request),
                        message="error: The diagnostic extraction fail"
                    )
                    return Response({'error': 'The diagnostic extraction fail'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            extra_max = 0.2*maximum/100
            intervals = round((maximum - minimum) / polygons, 8)
            lats, lons = latlon_coords(diag)

            figure = plt.figure()
            ax = figure.add_subplot(111)
            plt.close('all')
            lvl = np.around(np.arange(minimum, maximum + extra_max, intervals), 4)
            contourf = ax.contourf(lons, lats, diag, levels=lvl, cmap=map_palet)

            geojson = geojsoncontour.contourf_to_geojson(
                contourf=contourf,
                min_angle_deg=3.0,
                ndigits=3,
                stroke_width=1,
                fill_opacity=0.5,
            )

            data_time = diag.Time.values
            response = {
                'geojson': geojson,
                'max_index': max_index,
                'date_time': pd.to_datetime(data_time),
                'lat': round(diag.projection.moad_cen_lat, 0),
                'lon': round(diag.projection.stand_lon, 0),
                'maximum': maximum_default,
                'minimum': minimum_default,
                'success': 'The data went process',
            }

            Logs.objects.create(
                action='2d_maps_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success: The data went process"
            )
            for file in wrfout:
                file.close()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='2d_maps_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrossSections(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            urls = data.get('url')
            index = data.get('index')
            diagnostic = MAPS_RESULT_2D.get(data.get('diagnostic'))
            units = MAPS_UNITS_LABEL.get(data.get('units'))

            if not urls:
                Logs.objects.create(
                    action='cross_section_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No url data"
                )
                return Response({'error': 'No url data'}, status=status.HTTP_400_BAD_REQUEST)
            if not diagnostic:
                Logs.objects.create(
                    action='cross_section_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No diagnostic data"
                )
                return Response({'error': 'No diagnostic data'}, status=status.HTTP_400_BAD_REQUEST)
            if index is None:
                Logs.objects.create(
                    action='cross_section_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No index data"
                )
                return Response({'error': 'No index data'}, status=status.HTTP_400_BAD_REQUEST)
            if not units:
                Logs.objects.create(
                    action='cross_section_data',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='400',
                    ip=get_user_ip(self.request),
                    message="error: No units data"
                )
                return Response({'error': 'No units data'}, status=status.HTTP_400_BAD_REQUEST)

            wrfout = [Dataset(url) for url in urls]
            if data.get('diagnostic') in DEFAULT_UNIT_DIAGNOSTICS:
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

            Logs.objects.create(
                action='cross_section_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success: The data went process"
            )

            for file in wrfout:
                file.close()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='cross_section_data',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetMaxMinData(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, username):
        worker = Worker.objects.filter(user__username=username).first()
        try:
            diagnostics = Diagnostic.objects.filter(worker=worker)
            data = []

            for diagnostic in MAPS_DIAGNOSTICS_2D_LABEL.keys():
                max_min = create_max_min_data(diagnostic, diagnostics)
                data.append(max_min)

            return Response(data, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Files manager endpoints ----------------------------------------------------------------------------------------------


class GetListFiles(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        WRFoutFile.refresh_list_of_files()
        data = self.request.data
        try:
            list_file = []
            for file in WRFoutFile.objects.all().order_by(data.get('order')):
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
            Logs.objects.create(
                action='get_list_files',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success"
            )
            return Response(list_file, status=status.HTTP_200_OK)
        except:
            Logs.objects.create(
                action='get_list_files',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveFile(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            file = data.get('file')
            file_name = file.name.replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(':', '')
            content = Content.objects.first()

            valid_space = (content.server_space - WRFoutFile.get_used_space()) - round(file.size/1000000000, 2)

            if valid_space >= 0:
                if not WRFoutFile.objects.filter(name=file_name).first():
                    wrf_data = WRFoutFile.objects.create(
                        name=file_name,
                        path_file=file,
                        size=round(file.size/1000000, 2)
                    )

                    try:
                        Dataset(wrf_data.path_file.path)
                    except:
                        os.remove(f"{BASE_DIR}/wrfout_files/{wrf_data.name}")
                        wrf_data.delete()
                        Logs.objects.create(
                            action='save_file',
                            username=data.get('username'),
                            metadata=get_serialized_meta_data(self.request),
                            status_code='406',
                            ip=get_user_ip(self.request),
                            message="error: This type of file is not compatible"
                        )
                        return Response({'error': 'This type of file is not compatible'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                    Logs.objects.create(
                        action='save_file',
                        username=data.get('username'),
                        metadata=get_serialized_meta_data(self.request),
                        status_code='201',
                        ip=get_user_ip(self.request),
                        message="success: The was uploaded"
                    )
                    return Response({'success': 'The was uploaded'}, status=status.HTTP_201_CREATED)
                else:
                    Logs.objects.create(
                        action='save_file',
                        username=data.get('username'),
                        metadata=get_serialized_meta_data(self.request),
                        status_code='208',
                        ip=get_user_ip(self.request),
                        message="warning: This file already exist"
                    )
                    return Response({'warning:' 'This file already exist'}, status=status.HTTP_208_ALREADY_REPORTED)
            else:
                Logs.objects.create(
                    action='save_file',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='507',
                    ip=get_user_ip(self.request),
                    message="error: There is no space on the server"
                )
                return Response({'error': 'There is no space on the server'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        except:
            Logs.objects.create(
                action='save_file',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteFile(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            os.remove(f"{BASE_DIR}/wrfout_files/{data.get('file_name')}")
            Logs.objects.create(
                action='delete_file',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success: The file was deleted"
            )
            return Response({'success': 'The file was deleted'}, status=status.HTTP_200_OK)
        except:
            Logs.objects.create(
                action='delete_file',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Worker diagnostic data endpoints -------------------------------------------------------------------------------------


class SaveDiagnostic(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            worker = Worker.objects.filter(user__email=data['username']).first()
            geojson = data.get('geojson')
            lat = data.get('lat')
            lon = data.get('lon')
            diagnostic = data.get('diagnostic')
            map_palet = data.get('map_palet')
            maximum = data.get('maximum')
            minimum = data.get('minimum')
            date_time = data.get('date_time')
            units = data.get('units')
            polygons = data.get('polygons')
            file_name = data.get('file_name')
            z = data.get('z')
            x = data.get('x')
            y = data.get('y')
            x_min = data.get('minX')
            x_max = data.get('maxX')
            y_min = data.get('minY')
            y_max = data.get('maxY')

            diagnostics = Diagnostic.objects.filter(worker=worker)
            if not diagnostics.filter(file_name=file_name).first():
                Diagnostic.objects.create(
                    worker=worker,
                    geojson=geojson,
                    lat=lat,
                    lon=lon,
                    diagnostic=diagnostic,
                    map_palet=map_palet,
                    maximum=maximum,
                    minimum=minimum,
                    date_time=date_time,
                    unit=units,
                    polygons=polygons,
                    file_name=file_name,
                    z=z,
                    x=x,
                    y=y,
                    min_x=x_min,
                    max_x=x_max,
                    min_y=y_min,
                    max_y=y_max
                )
                Logs.objects.create(
                    action='save_diagnostic',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='201',
                    ip=get_user_ip(self.request),
                    message="success: A map data was save with success"
                )
                return Response({'success': 'A map data was save with success'}, status=status.HTTP_201_CREATED)
            else:
                Logs.objects.create(
                    action='save_diagnostic',
                    username=data.get('username'),
                    metadata=get_serialized_meta_data(self.request),
                    status_code='208',
                    ip=get_user_ip(self.request),
                    message="error: Diagnostic was already save"
                )
                return Response({'error': 'Diagnostic was already save'}, status=status.HTTP_208_ALREADY_REPORTED)
        except Exception as error_general:
            print(error_general)
            Logs.objects.create(
                action='save_diagnostic',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetDiagnosticList(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            worker = Worker.objects.filter(user__email=data.get('username')).first()
            diagnostics = Diagnostic.objects.filter(worker=worker).order_by(data.get('order_element'))
            response = []
            for diagnostic in diagnostics:
                response.append({
                    'diagnostic_id': diagnostic.id,
                    'diagnostic_label': MAPS_DIAGNOSTICS_2D_LABEL[diagnostic.diagnostic],
                    'units_label': MAPS_UNITS_TAGS[diagnostic.unit],
                    'map_palet': diagnostic.map_palet,
                    'file_name': diagnostic.file_name,
                    'diagnostic': diagnostic.diagnostic,
                    'date_time': diagnostic.date_time,
                    'units': diagnostic.unit,
                })

            Logs.objects.create(
                action='get_diagnostics',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success"
            )
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            Logs.objects.create(
                action='get_diagnostics',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetDiagnostic(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            diagnostic_id = data.get('diagnostic_id')
            diagnostic = Diagnostic.objects.filter(id=diagnostic_id).first()
            response = {
                    'geojson': diagnostic.geojson,
                    'lat': diagnostic.lat,
                    'lon': diagnostic.lon,
                    'diagnostic_label': MAPS_DIAGNOSTICS_2D_LABEL[diagnostic.diagnostic],
                    'units_label': MAPS_UNITS_TAGS[diagnostic.unit],
                    'map_palet': diagnostic.map_palet,
                    'polygons': diagnostic.polygons,
                    'file_name': diagnostic.file_name,
                    'diagnostic': diagnostic.diagnostic,
                    'date_time': diagnostic.date_time,
                    'units': diagnostic.unit,
                    'data': diagnostic.z,
                    'x': diagnostic.x,
                    'y': diagnostic.y,
                    'min_x': diagnostic.min_x,
                    'max_x': diagnostic.max_x,
                    'min_y': diagnostic.min_y,
                    'max_y': diagnostic.max_y
                }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteDiagnostic(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        try:
            worker = Worker.objects.filter(user__email=data.get('username')).first()
            diagnostic = Diagnostic.objects.filter(file_name=data.get('file_name'), worker=worker).first()
            diagnostic.delete()

            Logs.objects.create(
                action='delete_diagnostic',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='200',
                ip=get_user_ip(self.request),
                message="success: Diagnostic data deleted"
            )
            return Response({'success': 'Diagnostic data deleted'}, status=status.HTTP_200_OK)
        except:
            Logs.objects.create(
                action='delete_diagnostic',
                username=data.get('username'),
                metadata=get_serialized_meta_data(self.request),
                status_code='500',
                ip=get_user_ip(self.request),
                message="error: Something went wrong"
            )
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Contents endpoint ----------------------------------------------------------------------------------------------------

class GetContent(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            content = Content.objects.first()
            response = {
                'site_title': content.site_title,
                'server_space': content.server_space,
                'used_space': WRFoutFile.get_used_space(),
                'icon': content.icon_name,
                'favicon': content.favicon_name,
                'home_image': content.home_top_image_name,
                'card_diagnostics_image': content.card_diagnostics_image_name,
                'card_my_diagnostics_image': content.card_my_diagnostics_image_name,
                'home_content': content.home_content,
                'card_diagnostics': content.card_diagnostics,
                'card_my_diagnostics': content.card_my_diagnostics,
                'help_content': content.help_content
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetIcon(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, filename):
        try:
            image_path = os.path.join(MEDIA_ICONS_URL, filename)
            try:
                with open(image_path, 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/jpg')
            except:
                with open(f'{MEDIA_ICONS_URL}/default.png', 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/svg')
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetImage(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, filename):
        try:
            image_path = os.path.join(MEDIA_IMAGES_URL, filename)
            try:
                with open(image_path, 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/jpg')
            except:
                with open(f'{MEDIA_IMAGES_URL}/default.png', 'rb') as img:
                    return HttpResponse(img.read(), content_type='image/svg')
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
