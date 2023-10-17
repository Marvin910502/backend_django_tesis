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
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from api.models import WRFoutFileList

# WRF libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
from wrf import getvar, latlon_coords

# Selectors
from api.type_data import MAPS_RESULT_2D


# Auth endpoints -------------------------------------------------------------------------------------------------------


class CheckAuthenticatedView(APIView):
    def get(self, request):
        user = self.request.user

        try:
            is_authenticated = user.is_authenticated

            if is_authenticated:
                return Response({'isAuthenticated': 'success'})
            else:
                return Response({'isAuthenticated': 'error'})
        except:
            return Response({'error': 'Something went wrong when checking authentication status'})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({'success': 'CSRF cookie set'}, headers={'Set-Cookie': f'csrftoken={get_token(request)}; domain=http://127.0.0.1:8000'})


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data

        username = data['username']
        password = data['password']

        if User.objects.filter(username=username).first():
            return Response({'error': 'User already exists'})
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=username
            )

            return Response({"success": "User create successfully"}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data

        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({'success': 'User authenticated', 'username': username})
        else:
            return Response({'error': 'Error Authenticating'})


class LogoutView(APIView):
    def post(self, request):
        try:
            logout(request)
            return Response({'success': 'Loggout Out'})
        except:
            return Response({'error': 'Something went wrong when logging out'})


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
            section_amount = data.get('section_amount')

            wrfout = [Dataset(url) for url in urls]
            if 'default' in units:
                diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index)
            else:
                diag = getvar(wrfin=wrfout, varname=diagnostic, timeidx=index, units=units)
            maximum = round(diag.data.max(), 8)
            minimum = round(diag.data.min(), 8)
            extra_max = 0.2*maximum/100
            intervals = round((maximum - minimum) / section_amount, 8)
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
            return Response({'succes': 'Something went wrong'}, status=500)


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
