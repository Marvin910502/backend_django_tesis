from django.urls import path
from api.views import RegisterView, LoadUserView, LoginUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView

urlpatterns = [
    # Auth endpoints
    path('login/', LoginUserView.as_view(), name='api_user_login'),
    path('register/', RegisterView.as_view(), name='api_user_registration'),
    # path('login_required/', endpoints.api_login_required, name='api_login_required'),
    path('account/user/', LoadUserView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    # Plot data endpoints
]