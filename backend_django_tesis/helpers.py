import requests

from backend_django_tesis.initial_data import initial_content, admin_user, palettes, units, diagnostic_types
from django.contrib.auth.models import User
from django.core.files import File
from workers.models import Worker
from manager.models import Content
from wrf_logic.models import Palette, Unit, DiagnosticType


def populate_database():
    user = User.objects.create_user(
        username=admin_user['username'],
        email=admin_user['username'],
        password=admin_user['password']
    )

    Worker.objects.create(
        user=user,
        isAdmin=admin_user['is_admin'],
        isGuess=admin_user['is_guess'],
        isManager=admin_user['is_manager'],
        department=admin_user['department']
    )

    icon = initial_content['icon']
    favicon = initial_content['favicon']
    home_top_image = initial_content['home_top_image']
    card_diagnostics_image = initial_content['card_diagnostics_image']
    card_my_diagnostics_image = initial_content['card_my_diagnostics_image']

    content = Content.objects.create(
        site_title=initial_content['site_title'],
        server_space=initial_content['server_space'],
        icon_name=initial_content['icon_name'].replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
        favicon_name=initial_content['favicon_name'].replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
        home_top_image_name=initial_content['home_top_image_name'].replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
        card_diagnostics_image_name=initial_content['card_diagnostics_image_name'].replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
        card_my_diagnostics_image_name=initial_content['card_my_diagnostics_image_name'].replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', ''),
        home_content=initial_content['home_content'],
        card_diagnostics=initial_content['card_diagnostics'],
        card_my_diagnostics=initial_content['card_my_diagnostics'],
        help_content=initial_content['help_content']
    )

    with open(icon, 'rb') as file:
        content.icon.save(initial_content['icon_name'], File(file), save=True)
    with open(favicon, 'rb') as file:
        content.favicon.save(initial_content['favicon_name'], File(file), save=True)
    with open(home_top_image, 'rb') as file:
        content.home_top_image.save(initial_content['home_top_image_name'], File(file), save=True)
    with open(card_diagnostics_image, 'rb') as file:
        content.card_diagnostics_image.save(initial_content['card_diagnostics_image_name'], File(file), save=True)
    with open(card_my_diagnostics_image, 'rb') as file:
        content.card_my_diagnostics_image.save(initial_content['card_my_diagnostics_image_name'], File(file), save=True)


def populate_diagnostic_data():
    for palette in palettes:
        Palette.objects.create(
            name=palette['label'],
            type=palette['type']
        )
    for unit in units:
        Unit.objects.create(
            name=unit['name'],
            symbol=unit['symbol']
        )
    for diagnostic_type in diagnostic_types:
        diagnostic_type_instance = DiagnosticType.objects.create(
            name=diagnostic_type['name'],
            value=diagnostic_type['value']
        )
        for unit in diagnostic_type['unit_ids']:
            unit_instance = Unit.objects.get(id=unit)
            diagnostic_type_instance.unit_ids.add(unit_instance)
        diagnostic_type_instance.save()