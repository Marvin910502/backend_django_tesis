import json

from django.test import TestCase

# Create your tests here.

from django.test import Client, TestCase
from django.urls import reverse, NoReverseMatch
from backend_django_tesis.settings import BASE_DIR


class APITestCase(TestCase):
    def setUp(self):
        self.worker_data = {
            'email': 'test_email@test_server.com',
            'password': 't35t_p455w0rd',
        }
        self.file_test_data = {
            'url': [f'{BASE_DIR}/api/test_file/wrfout_d01_2005-08-28_00_00_00'],
            'diagnostic': 'presion_nivel_del_mar',
            'index': 0,
            'units': 'hPa',
            'polygons': 10
        }

    def perform_registration_endpoint(self):
        body = {
            'username': self.worker_data['email'],
            'password': self.worker_data['password']
        }
        response = self.client.post(
            path=reverse('register'),
            data=body,
            format='json',
        )
        return response

    def perform_registration_double_user(self):
        body = {
            'username': self.worker_data['email'],
            'password': self.worker_data['password']
        }
        response = self.client.post(
            path=reverse('register'),
            data=body,
            format='json',
        )
        return response

    def perform_get_user_data_endpoint(self):
        body = {
            'username': self.worker_data['email']
        }
        response = self.client.post(
            path=reverse('get_user'),
            data=body,
            format='json',
        )
        return response

    def perform_update_user_endpoint(self):
        body = {
            'old_username': self.worker_data['email'],
            'username': 'user_update_test@test_server.com',
            'name': 'test_name',
            'last_names': 'test_last_names',
            'department': 'test_department'
        }
        response = self.client.post(
            path=reverse('update_user'),
            data=body,
            format='json'
        )
        return response

    def perform_change_password_endpoint(self, body):
        response = self.client.post(
            path=reverse('change_passwd'),
            data=body,
            format='json'
        )
        return response

    def perform_two_dimensional_variables_map_endpoint(self, body):
        response = self.client.post(
            path=reverse('2d_variables_maps'),
            data=json.dumps(body),
            content_type='application/json'
        )
        return response

    def perform_cross_sections_endpoint(self, body):
        response = self.client.post(
            path=reverse('cross_sections'),
            data=json.dumps(body),
            content_type='application/json'
        )
        return response

    def test_registration_success(self):
        response = self.perform_registration_endpoint()
        self.assertEquals(response.status_code, 201)

    def test_registration_duplicate_user(self):
        self.perform_registration_endpoint()
        response = self.perform_registration_double_user()
        self.assertEquals(response.status_code, 401)

    def test_get_user(self):
        self.perform_registration_endpoint()
        response = self.perform_get_user_data_endpoint()
        self.assertEquals(response.status_code, 200)

    def test_update_user(self):
        self.perform_registration_endpoint()
        response = self.perform_update_user_endpoint()
        self.assertEquals(response.status_code, 201)

    def test_change_password(self):
        self.perform_registration_endpoint()
        body = {
            'username': self.worker_data['email'],
            'old_password': self.worker_data['password'],
            'new_password': 'n3w_p1sswo4d'
        }
        response = self.perform_change_password_endpoint(body)
        self.assertEquals(response.status_code, 201)

    def test_change_password_wrong(self):
        self.perform_registration_endpoint()
        body = {
            'username': self.worker_data['email'],
            'old_password': 'wrong_password',
            'new_password': 'n3w_p1sswo4d'
        }
        response = self.perform_change_password_endpoint(body)
        self.assertEquals(response.status_code, 401)

    def test_2d_maps_endpoint(self):
        response = self.perform_two_dimensional_variables_map_endpoint(self.file_test_data)
        self.assertEquals(response.status_code, 200)

    def test_cross_section(self):
        response = self.perform_cross_sections_endpoint(self.file_test_data)
        self.assertEquals(response.status_code, 200)
