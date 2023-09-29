from django.urls import path
from api import endpoints


urlpatterns = [
    path('login/', endpoints.api_login_user, name='api_send_token'),
    path('register/', endpoints.api_user_registration, name='api_user_registration'),
]