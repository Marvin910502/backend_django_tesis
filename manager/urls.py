from django.urls import path
from manager import views


urlpatterns = [
    path('', views.login_admin, name='login_admin'),
    path('logout/', views.logout_admin, name='logout_admin'),
    path('usuarios/', views.manage_users, name='users'),
    path('editar-usuario/<str:uuid>/', views.manage_edit_user, name='manager_edit_user'),
    path('crear-usuario/', views.manage_create_user, name='manager_create_user'),
    path('eliminar-usuario/<str:uuid>/', views.manage_delete_user, name='manager_delete_user'),
    path('contenidos/', views.manage_contents, name='manager_contents'),
    path('configuraciones', views.manage_configurations, name='manager_configuration'),
    path('delete-images-site/<str:image>/', views.delete_image_site, name='delete_images_site'),
    path('registros/<str:order>/<int:index>/<str:filter_search>/', views.logs, name='logs')
]
