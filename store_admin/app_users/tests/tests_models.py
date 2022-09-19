from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_products.models import Product
from app_users.tests.settings import USERNAME, PASSWORD
from app_users.models import Profile, Feedback


class BaseModelTest(TestCase):
    fixtures = \
        ['app_users/tests/fixtures/fixtures_test_users_model.json']

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

        product = Product.objects.first()
        cls.user = user
        cls.profile = Profile.objects.create(tel_number='9165236894',
                                             patronymic='patronymic',
                                             avatar='avatar',
                                             user_fk=user)

        cls.feedback = Feedback.objects.create(text='text',
                                               product_fk=product,
                                               user_fk=user)


class TestProfile(BaseModelTest):
    def test_tel_number_label(self) -> None:
        """Проверка подписи поля номера телефона"""
        field_label = self.profile._meta.get_field('tel_number').verbose_name
        self.assertEquals(field_label, _('telephone number'))

    def test_patronymic_label(self) -> None:
        """Проверка подписи поля отчества"""
        field_label = self.profile._meta.get_field('patronymic').verbose_name
        self.assertEquals(field_label, _('patronymic'))

    def test_avatar_label(self) -> None:
        """Проверка подписи поля аватар"""
        field_label = self.profile._meta.get_field('avatar').verbose_name
        self.assertEquals(field_label, _('avatar'))

    def test_user_label(self) -> None:
        """Проверка подписи поля пользователь"""
        field_label = self.profile._meta.get_field('user_fk').verbose_name
        self.assertEquals(field_label, _('user'))


class TestFeedback(BaseModelTest):
    def test_text_label(self) -> None:
        """Проверка подписи поля теста отзыва"""
        field_label = self.feedback._meta.get_field('text').verbose_name
        self.assertEquals(field_label, _('text'))

    def test_product_label(self) -> None:
        """Проверка подписи поля товара"""
        field_label = self.feedback._meta.get_field('product_fk').verbose_name
        self.assertEquals(field_label, _('product'))

    def test_user_label(self) -> None:
        """Проверка подписи поля пользователь"""
        field_label = self.feedback._meta.get_field('user_fk').verbose_name
        self.assertEquals(field_label, _('user'))
