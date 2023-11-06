from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from backend_django_tesis.settings import LOGIN_URL

from workers.models import Worker, Diagnostic
from api.models import WRFoutFileList
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
    files = WRFoutFileList.objects.all()

    data = {
        'workers': workers,
        'diagnostics': diagnostics,
        'files': files
    }
    return data


def login_admin(request):
    message, class_alert = check_session_message(request)

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

    context = {
        'workers': data.get('workers'),
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': 500,
        'storage_used': 45,
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'users.html', context)


@login_required(login_url=LOGIN_URL)
def manage_edit_user(request, uuid):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    workers = data.get('workers')
    worker = workers.filter(uuid=uuid).first()
    user = User.objects.filter(username=worker.user).first()
    if request.method == 'POST':
        request_post = request.POST

        if 'change_password' in request_post:
            old_password = request_post.get('old_password')
            password = request_post.get('password')
            re_password = request_post.get('password')
            if authenticate(username=user.username, password=old_password):
                if password == re_password:
                    user.set_password(password)
                    user.save()
                    message = 'La contraseña fue actualizada con éxito'
                    class_alert = SUCCESS_MESSAGE
                else:
                    message = 'Las contraseña nueva no coincide con la repetida'
                    class_alert = DANGER_MESSAGE
            else:
                message = 'La contraseña actual es incorrecta'
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

    context = {
        'worker': worker,
        'departments': department_list,
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': 500,
        'storage_used': 45,
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'edit_user.html', context)


@login_required(login_url=LOGIN_URL)
def manage_create_user(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()

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
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': 500,
        'storage_used': 45,
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'create_user.html', context)


@login_required(login_url=LOGIN_URL)
def manage_delete_user(request, uuid):
    worker = Worker.objects.filter(uuid=uuid).first()
    user = User.objects.filter(username=worker.user).first()
    user.delete()
    worker.delete()
    request.session['message'] = 'El usuario ha sido eliminado con éxito'
    request.session['class_alert'] = SUCCESS_MESSAGE
    return redirect('users')


@login_required(login_url=LOGIN_URL)
def manage_contents(request):
    message, class_alert = check_session_message(request)
    data = amounts_data()

    content = Content.objects.first()
    text = content.help_content
    if request.method == 'POST':
        request_post = request.POST
        text = request_post.get('text_editor')
        content.help_content = text
        content.save()

    context = {
        'text': text,
        'users_amount': data.get('workers').__len__(),
        'diagnostics_amount': data.get('diagnostics').__len__(),
        'files_amount': data.get('files').__len__(),
        'storage_space': 500,
        'storage_used': 45,
        'message': message,
        'class_alert': class_alert
    }
    return render(request, 'contents.html', context)
