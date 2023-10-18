from django.urls import path
from api.endpoints import RegisterView, TwoDimensionsVariablesMaps, GetListFiles, GetUserData
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
    path('get-wrfout-list/', GetListFiles.as_view())
]