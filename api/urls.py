from django.urls import path
from api.endpoints import (
                           RegisterView,
                           TwoDimensionsVariablesMaps,
                           GetListFiles,
                           GetUserData,
                           SaveMapData,
                           GetListMapData,
                           DeleteMapData,
                           SaveFile,
                           DeleteFile,
                           CrossSections,
                           UpdateUser,
                           ChangePasswd,
                           GetContent
                          )
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
    path('register/', RegisterView.as_view(), name='register'),
    path('get-user/', GetUserData.as_view(), name='get_user'),
    path('update-user/', UpdateUser.as_view(), name='update_user'),
    path('change-passwd/', ChangePasswd.as_view(), name='change_passwd'),
    # Plot data endpoints
    path('2d-variables-maps/', TwoDimensionsVariablesMaps.as_view(), name='2d_variables_maps'),
    path('cross-sections/', CrossSections.as_view(), name='cross_sections'),
    # File manager endpoints
    path('get-wrfout-list/', GetListFiles.as_view(), name='get_wrfout_list'),
    path('upload-file/', SaveFile.as_view(), name='upload_file'),
    path('delete-file/', DeleteFile.as_view(), name='delete_file'),
    # Worker data endpoints
    path('save-map-data/', SaveMapData.as_view(), name='save_map_data'),
    path('get-list-map-data/', GetListMapData.as_view(), name='get_list_map_data'),
    path('delete-map-data/', DeleteMapData.as_view(), name='delete_map_data'),
    # Content data endpoints
    path('get-content/', GetContent.as_view(), name='get_content')
]
