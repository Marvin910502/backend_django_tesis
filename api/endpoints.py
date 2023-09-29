import json

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from api.models import UserToken


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def api_login_user(request):
    status_code = 401
    response = {
        'success': False,
        'token': '',
        'message': 'The request failed',
    }

    if request.method == 'POST':
        request_body = json.loads(request.body)
        user = User.objects.filter(username=request_body['username']).first()
        if authenticate(username=request_body['username'], password=request_body['password']):
            login(request, user)
            response['success'] = True
            response['token'] = user.usertoken_set.first().token
            response['message'] = 'The user login was successfully'
            status_code = 200
            return Response(response, status=status_code)
    return Response(response, status=status_code)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def api_user_registration(request):
    response = {
        'success': False,
        'message': 'The request failed'
    }

    status_code = 401

    if request.method == 'POST':
        request_body = json.loads(request.body)
        user = User.objects.create(
            username=request_body['username']
        )
        user.set_password(request_body['password'])
        user.save()
        UserToken.objects.create(user=user)
        status_code = 200
        response['success'] = True
        response['message'] = 'The user was registered with success'
        return Response(response, status=status_code)

    return Response(response, status=status_code)
