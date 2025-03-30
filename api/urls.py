from django.urls import path
from api.endpoints import (
    RegisterView,
    TwoDimensionsVariablesMaps,
    GetListFiles,
    GetUserData,
    SaveDiagnostic,
    GetDiagnostic,
    GetDiagnosticList,
    DeleteDiagnostic,
    SaveFile,
    DeleteFile,
    CrossSections,
    UpdateUser,
    ChangePasswd,
    GetContent,
    UploadProfileImage,
    GetProfileImage,
    GetIcon,
    GetImage,
    GetMaxMinData,
    TestAuthView
)
from api.views import PruebaError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # Auth endpoints
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', RegisterView.as_view(), name='register'),
    path('get-user/', GetUserData.as_view(), name='get_user'),
    path('update-user/', UpdateUser.as_view(), name='update_user'),
    path('upload-profile-image/', UploadProfileImage.as_view(), name='upload_profile_image'),
    path('media/get-profile-image/<str:filename>', GetProfileImage.as_view(), name='get_profile_image'),
    path('change-passwd/', ChangePasswd.as_view(), name='change_passwd'),
    # Plot data endpoints
    path('2d-variables-maps/', TwoDimensionsVariablesMaps.as_view(), name='2d_variables_maps'),
    path('cross-sections/', CrossSections.as_view(), name='cross_sections'),
    path('get-max-min/<str:username>/', GetMaxMinData.as_view(), name='get_max_min'),
    # File manager endpoints
    path('get-wrfout-list/', GetListFiles.as_view(), name='get_wrfout_list'),
    path('upload-file/', SaveFile.as_view(), name='upload_file'),
    path('delete-file/', DeleteFile.as_view(), name='delete_file'),
    # Worker data endpoints
    path('save-diagnostic/', SaveDiagnostic.as_view(), name='save_map_data'),
    path('get-diagnostic-list/', GetDiagnosticList.as_view(), name='get_list_map_data'),
    path('get-diagnostic/', GetDiagnostic.as_view(), name='get_diagnostic'),
    path('delete-diagnostic/', DeleteDiagnostic.as_view(), name='delete_map_data'),
    # Content data endpoints
    path('get-content/', GetContent.as_view(), name='get_content'),
    path('media/get-icon/<str:filename>', GetIcon.as_view(), name='get-icon'),
    path('media/get-image/<str:filename>', GetImage.as_view(), name='get-image'),
    # PruebaError
    path('prueba-error/', PruebaError.as_view(), name='prueba_error'),
]
