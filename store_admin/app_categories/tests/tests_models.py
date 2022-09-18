from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_categories.models import Category, Feature
from app_categories.tests.settings import FEATURE, CATEGORY


class BaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        cls.feature = Feature.objects.create(**FEATURE)
        cls.category = Category.objects.create(**CATEGORY)


class FeatureTest(BaseModelTest):
    def test_name_label(self) -> None:
        """Проверка подписи поля названия характеристики"""
        field_label = self.feature._meta.get_field('name').verbose_name
        self.assertEquals(field_label, _('name'))

    def test_slug_label(self) -> None:
        """Проверка подписи поля slug характеристики"""
        field_label = self.feature._meta.get_field('slug').verbose_name
        self.assertEquals(field_label, _('slug'))

    def test_type_feature_label(self) -> None:
        """Проверка подписи поля типа характеристики"""
        field_label = self.feature._meta.get_field('type_feature').verbose_name
        self.assertEquals(field_label, _('type feature'))


class CategoryTest(BaseModelTest):
    def test_name_label(self) -> None:
        """Проверка подписи поля названия категории"""
        field_label = self.category._meta.get_field('name').verbose_name
        self.assertEquals(field_label, _('name'))

    def test_icon_label(self) -> None:
        """Проверка подписи поля иконки категории"""
        field_label = self.category._meta.get_field('icon').verbose_name
        self.assertEquals(field_label, _('icon'))

    def test_is_active_label(self) -> None:
        """Проверка подписи поля активности категории"""
        field_label = self.category._meta.get_field('is_active').verbose_name
        self.assertEquals(field_label, _('is active'))

    def test_parent_label(self) -> None:
        """Проверка подписи поля вложенности категории"""
        field_label = self.category._meta.get_field('parent').verbose_name
        self.assertEquals(field_label, _('put in category'))
