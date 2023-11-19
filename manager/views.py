import os
import uuid

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from backend_django_tesis.settings import LOGIN_URL, MEDIA_PROFILES_URL, MEDIA_ICONS_URL, MEDIA_IMAGES_URL

from workers.models import Worker, Diagnostic
from api.models import WRFoutFile
from manager.models import Content
from django.contrib.auth.models import User

# Create your views here.
SUCCESS_MESSAGE = 'success'
WARNING_MESSAGE = 'warning'
INFO_MESSAGE = 'info'
DANGER_MESSAGE = 'danger'

department_list = ['Visitante', 'Informática', 'Física de la Atmósfera', 'Pronósticos', 'Radares', 'Estudiante']


def check_session_message(request):
    """returns (if exists) any message and its class style stored in current request session."""
    if 'message' in request.session and 'class_alert' in request.session:
        message, class_alert = request.session.get('message'), request.session.get('class_alert')
        del request.session['message']
        del request.session['class_alert']
        return message, class_alert
    else:
        return None, None


def amounts_data():
    workers = Worker.objects.all()
    diagnostics = Diagnostic.objects.all()
    files = WRFoutFile.objects.all()
    content = Content.objects.first()

    used_space = WRFoutFile.get_used_space()
    free_space = 100 - (used_space*100/content.server_space)

    low_space = False

    if free_space < 10:
        low_space = True

    data = {
        'workers': workers,
        'diagnostics': diagnostics,
        'files': files,
        'used_space': used_space,
        'content': content,
        'low_space': low_space
    }
    return data


def login_admin(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()
    content = data.get('content')

    if request.user.is_authenticated:
        return redirect('users')

    if request.method == 'POST':
        request_post = request.POST
        email = request_post.get('email')
        password = request_post.get('password')
        user = User.objects.filter(username=email).first()
        worker = Worker.objects.filter(user=user).first()
        if authenticate(username=email, password=password):
            if worker.isAdmin:
                login(request, user)
                return redirect('users')
            else:
                message = 'El usuario no es administrador'
                class_alert = DANGER_MESSAGE
        else:
            message = 'Correo o contraseña incorrecta'
            class_alert = DANGER_MESSAGE

    context = {
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'login.html', context)


def logout_admin(request):
    logout(request)
    return redirect('login_admin')


@login_required(login_url=LOGIN_URL)
def manage_users(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    content = data.get('content')

    context = {
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'workers': data.get('workers'),
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'users.html', context)


@login_required(login_url=LOGIN_URL)
def manage_edit_user(request, uuid):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    content = data.get('content')

    workers = data.get('workers')
    worker = workers.filter(uuid=uuid).first()
    user = User.objects.filter(username=worker.user).first()
    email = user.email
    if request.method == 'POST':
        request_post = request.POST

        if 'change_password' in request_post:
            password = request_post.get('password')
            re_password = request_post.get('password')
            if password == re_password:
                user.set_password(password)
                user.save()
                message = 'La contraseña fue actualizada con éxito'
                class_alert = SUCCESS_MESSAGE
                if worker.isAdmin:
                    request.session['message'] = 'La contraseña fue actualizada con éxito'
                    request.session['class_alert'] = SUCCESS_MESSAGE
                    return redirect('login_admin')
            else:
                message = 'Las contraseña nueva no coincide con la repetida'
                class_alert = DANGER_MESSAGE

        if 'update_user' in request_post:
            email = request_post.get('email')
            name = request_post.get('name')
            last_names = request_post.get('last_names')
            department = request_post.get('department')
            is_guess = True if request_post.get('is_guess') else False
            is_manger = True if request_post.get('is_manager') else False
            is_admin = True if request_post.get('is_admin') else False
            user.email = email
            user.username = email
            user.save()
            worker.name = name
            worker.last_names = last_names
            worker.department = department
            worker.isGuess = is_guess
            worker.isManager = is_manger
            worker.isAdmin = is_admin
            worker.save()
            message = 'Los datos del usuario han sido actualizados'
            class_alert = SUCCESS_MESSAGE
        if request_post.get('email') and worker.isAdmin:
            return redirect('logout_admin')

    context = {
        'email': email,
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'worker': worker,
        'departments': department_list,
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'edit_user.html', context)


@login_required(login_url=LOGIN_URL)
def manage_create_user(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    content = data.get('content')

    email = ''
    name = ''
    last_names = ''
    department = ''
    is_guess = ''
    is_manager = ''
    is_admin = ''
    if request.method == 'POST':
        request_post = request.POST
        email = request_post.get('email')
        name = request_post.get('name')
        last_names = request_post.get('last_name')
        department = request_post.get('department')
        is_guess = True if request_post.get('is_guess') else False
        is_manager = True if request_post.get('is_manager') else False
        is_admin = True if request_post.get('is_admin') else False
        password = request_post.get('password')
        re_password = request_post.get('re_password')
        if password == re_password:
            if User.objects.filter(username=email).exists():
                message = 'El usuario ya existe'
                class_alert = DANGER_MESSAGE
            else:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
                Worker.objects.create(
                    user=user,
                    department=department,
                    name=name,
                    last_names=last_names,
                    isGuess=is_guess,
                    isManager=is_manager,
                    isAdmin=is_admin
                )
                request.session['message'] = 'El usuario ha sido creado con éxito'
                request.session['class_alert'] = SUCCESS_MESSAGE
                return redirect('users')
        else:
            message = 'Las contraseñas no coinciden'
            class_alert = DANGER_MESSAGE

    context = {
        'email': email,
        'name': name,
        'last_names': last_names,
        'department': department,
        'is_guess': is_guess,
        'is_manager': is_manager,
        'is_admin': is_admin,
        'departments': department_list,
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'create_user.html', context)


@login_required(login_url=LOGIN_URL)
def manage_delete_user(request, uuid):
    worker = Worker.objects.filter(uuid=uuid).first()
    user = User.objects.filter(username=worker.user).first()
    if worker.image_name:
        os.remove(f"{MEDIA_PROFILES_URL}/{worker.image_name}")
    user.delete()
    worker.delete()
    request.session['message'] = 'El usuario ha sido eliminado con éxito'
    request.session['class_alert'] = SUCCESS_MESSAGE
    return redirect('users')


@login_required(login_url=LOGIN_URL)
def manage_contents(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    content = data.get('content')
    home_content = content.home_content
    card_diagnostics = content.card_diagnostics
    card_my_diagnostics = content.card_my_diagnostics
    help_content = content.help_content
    if request.method == 'POST':
        request_post = request.POST
        home_content = request_post.get('home_content')
        card_diagnostics = request_post.get('card_diagnostics')
        card_my_diagnostics = request_post.get('card_my_diagnostics')
        help_content = request_post.get('help_content')
        content.home_content = home_content
        content.card_diagnostics = card_diagnostics
        content.card_my_diagnostics = card_my_diagnostics
        content.help_content = help_content
        content.save()

    context = {
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'home_content': home_content,
        'card_diagnostics': card_diagnostics,
        'card_my_diagnostics': card_my_diagnostics,
        'help_content': help_content,
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'contents.html', context)


@login_required(login_url=LOGIN_URL)
def manage_configurations(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()
    content = data.get('content')
    site_title = content.site_title
    server_space = content.server_space

    if request.method == 'POST':
        request_post = request.POST
        request_file = request.FILES
        site_title = request_post.get('site_title')
        server_space = request_post.get('server_space')
        icon = request_file.get('icon')
        favicon = request_file.get('favicon')
        home_top_image = request_file.get('home_top_image')
        card_diagnostics_image = request_file.get('card_diagnostics_image')
        card_my_diagnostics_image = request_file.get('card_my_diagnostics_image')
        content.server_space = server_space
        content.site_title = site_title
        if icon:
            if content.icon_name:
                try:
                    os.remove(f"{MEDIA_ICONS_URL}/{content.icon_name}")
                except Exception as error:
                    print(error)
            icon.name = uuid.uuid4().__str__()
            content.icon = icon
            content.icon_name = icon.name
        if favicon:
            if content.favicon_name:
                try:
                    os.remove(f"{MEDIA_ICONS_URL}/{content.favicon_name}")
                except Exception as error:
                    print(error)
            favicon.name = uuid.uuid4().__str__()
            content.favicon = favicon
            content.favicon_name = favicon.name
        if home_top_image:
            if content.home_top_image_name:
                try:
                    os.remove(f"{MEDIA_IMAGES_URL}/{content.home_top_image_name}")
                except Exception as error:
                    print(error)
            home_top_image.name = uuid.uuid4().__str__()
            content.home_top_image = home_top_image
            content.home_top_image_name = home_top_image.name
        if card_diagnostics_image:
            if content.card_diagnostics_image_name:
                try:
                    os.remove(f"{MEDIA_IMAGES_URL}/{content.card_diagnostics_image_name}")
                except Exception as error:
                    print(error)
            card_diagnostics_image.name = uuid.uuid4().__str__()
            content.card_diagnostics_image = card_diagnostics_image
            content.card_diagnostics_image_name = card_diagnostics_image.name
        if card_my_diagnostics_image:
            if content.card_my_diagnostics_image_name:
                try:
                    os.remove(f"{MEDIA_IMAGES_URL}/{content.card_my_diagnostics_image_name}")
                except Exception as error:
                    print(error)
            card_my_diagnostics_image.name = uuid.uuid4().__str__()
            content.card_my_diagnostics_image = card_my_diagnostics_image
            content.card_my_diagnostics_image_name = card_my_diagnostics_image.name
        content.save()
        data = amounts_data()

    context = {
        'server_space': server_space,
        'site_title': site_title,
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
        'home_top_image': content.home_top_image.url if content.home_top_image else '',
        'card_diagnostics_image': content.card_diagnostics_image.url if content.card_diagnostics_image else '',
        'card_my_diagnostics_image': content.card_my_diagnostics_image.url if content.card_my_diagnostics_image else '',
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'configurations.html', context)


@login_required(login_url=LOGIN_URL)
def delete_image_site(request, image):
    content = Content.objects.first()

    if image == 'icon':
        os.remove(f"{MEDIA_ICONS_URL}/{content.icon_name}")
        content.icon_name = ''
        content.icon = ''
        content.save()
    if image == 'favicon':
        os.remove(f"{MEDIA_ICONS_URL}/{content.favicon_name}")
        content.favicon_name = ''
        content.favicon = ''
        content.save()
    if image == 'home_image':
        os.remove(f"{MEDIA_IMAGES_URL}/{content.home_top_image_name}")
        content.home_top_image_name = ''
        content.home_top_image = ''
        content.save()
    if image == 'card_diagnostics':
        os.remove(f"{MEDIA_IMAGES_URL}/{content.card_diagnostics_image_name}")
        content.card_diagnostics_image_name = ''
        content.card_diagnostics_image = ''
        content.save()
    if image == 'card_my_diagnostics':
        os.remove(f"{MEDIA_IMAGES_URL}/{content.card_my_diagnostics_image_name}")
        content.card_my_diagnostics_image_name = ''
        content.card_my_diagnostics_image = ''
        content.save()

    return redirect('manager_configuration')


def page_404(request):
    data = amounts_data()
    content = data.get('content')

    context = {
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': data.get('content').server_space,
        'storage_used': data.get('used_space'),
        'low_space': data.get('low_space'),
        'icon': content.icon.url if content.icon else '',
        'favicon': content.favicon.url if content.favicon else '',
    }
    return render(request, 'page_404.html', context)
