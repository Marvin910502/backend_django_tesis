# Python libraries
import json

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

# WRF libraries
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import geojsoncontour
import numpy as np
from wrf import getvar, latlon_coords


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


# WRF endpoints --------------------------------------------------------------------------------------------------------


class TwoDimensionsVariablesMaps(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        try:
            data = self.request.data
            wrfout = Dataset(data['url'])
            slp = getvar(wrfout, 'slp', timeidx=0)
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

            status_code = 200
            response = {
                'geojson': geojson,
                'success': 'The data went process',
                'lvl': lvl,
                'max': max,
                'invert_lvl': invert_lvl,
            }

            return Response(response, status=status_code)
        except:
            return Response({'succes': 'Something went wrong'}, status=500)