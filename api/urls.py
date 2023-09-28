from django.urls import path
from api import endpoints


urlpatterns = [
    path('', endpoints.api_login_user, name='api_send_token'),
]