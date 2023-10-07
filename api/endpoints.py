import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from .serializers import UserSerializer


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

