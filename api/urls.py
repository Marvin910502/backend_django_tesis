from django.urls import path
from api.endpoints import RegisterView, TwoDimensionsVariablesMaps, GetListFiles, GetUserData, SaveMapData, GetListMapData, DeleteMapData, SaveFile, DeleteFile
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # Auth endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', RegisterView.as_view()),
    path('get-user/', GetUserData.as_view()),
    # Plot data endpoints
    path('2d-variables-maps/', TwoDimensionsVariablesMaps.as_view()),
    # File manager enpoints
    path('get-wrfout-list/', GetListFiles.as_view()),
    path('upload-file/', SaveFile.as_view()),
    path('delete-file/', DeleteFile.as_view()),
    # Worker data endpoints
    path('save-map-data/', SaveMapData.as_view()),
    path('get-list-map-data/', GetListMapData.as_view()),
    path('delete-map-data/', DeleteMapData.as_view())
]