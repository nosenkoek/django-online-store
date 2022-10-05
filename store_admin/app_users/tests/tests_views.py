from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import connection

from app_users.models import Profile
from app_users.tests.tests_models import BaseModelTest
from app_users.tests.settings import USERNAME, PASSWORD, DATA_USER


class RegisterTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(RegisterTest, cls).setUpClass()

    def setUp(self) -> None:
        self.main_url = '/users/register'

    def test_register_url(self):
        """Проверка открытия страницы регистрации"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_register_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(self.main_url, follow=True)
        self.assertTemplateUsed(response, 'app_users/register.html')

    def test_register(self):
        """Проверка регистрации пользователя"""
        response = self.client.post(reverse('register'),
                                    data=DATA_USER,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

        login_user = self.client.login(username=DATA_USER.get('username'),
                                       password=DATA_USER.get('password1'))
        self.assertTrue(login_user)
        user_db = User.objects.first()
        user = get_user(self.client)
        self.assertEqual(user, user_db)


class LoginTest(BaseModelTest):
    def setUp(self) -> None:
        self.main_url = '/users/login'

    def test_login_ulr(self):
        """ Проверка открытия страницы"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_login_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'app_users/login.html')

    def test_login(self):
        """Проверка входа"""
        data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        user_db = User.objects.get(username=USERNAME)

        self.client.get(reverse('login'), follow=True)
        response = self.client.post(reverse('login'), data, follow=True)
        self.assertRedirects(response, reverse('main_page'))
        user = get_user(self.client)
        self.assertEqual(user, user_db)


class LogoutTest(TestCase):
    def setUp(self) -> None:
        self.main_url = '/users/login'

    def test_logout(self):
        """Проверка выхода и перенаправления на главную"""
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get('/users/logout/', follow=True)
        self.assertRedirects(response, reverse('main_page'))

        user = get_user(self.client)
        self.assertTrue(user.is_anonymous)
