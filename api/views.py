from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        data = request.data

        username = data['username']
        password = data['password']

        User.objects.create_user(
            username=username,
            email=username,
            password=password
        )

        return Response({"success": "User create successfully"}, status=status.HTTP_201_CREATED)


class LoadUserView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request):
        try:
            user = request.user
            print(user)
            user = UserSerializer(user)
            return Response({"user": user.data}, status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong when trying load user'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUserView(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        try:
            data = request.data
            email = data['username']
            password = data['password']
            user = User.objects.filter(username=email).first()
            if authenticate(username=email, password=password):
                login(request, user)
                return Response({'success': 'User login in successfully'}, status.HTTP_200_OK)
        except:
            return Response({'error': 'Something went wrong when user try to login'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
