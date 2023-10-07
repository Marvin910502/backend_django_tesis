from django.urls import path
from wrf_app import views


urlpatterns = [
    path('', views.mapping, name='mapping'),
    # path('api-mapping/', views.api_mapping, name='api_mapping')
]