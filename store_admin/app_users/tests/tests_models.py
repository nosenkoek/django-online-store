from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_users.tests.settings import USERNAME, PASSWORD
from app_users.models import User


class BaseModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(BaseModelTest, cls).setUpClass()

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username=USERNAME)
        user.set_password(PASSWORD)
        user.save()
        cls.user = user


class TestUserFields(BaseModelTest):
    def test_tel_number_label(self) -> None:
        """Проверка подписи поля номера телефона"""
        field_label = self.user._meta.get_field('tel_number').verbose_name
        self.assertEquals(field_label, _('telephone number'))

    def test_patronymic_label(self) -> None:
        """Проверка подписи поля отчества"""
        field_label = self.user._meta.get_field('patronymic').verbose_name
        self.assertEquals(field_label, _('patronymic'))

    def test_avatar_label(self) -> None:
        """Проверка подписи поля аватар"""
        field_label = self.user._meta.get_field('avatar').verbose_name
        self.assertEquals(field_label, _('avatar'))
