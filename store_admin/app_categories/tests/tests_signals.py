from uuid import uuid4

from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_categories.models import Category, Feature, CategoryFeature

CATEGORY = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'category_name',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}

CATEGORY_NEW = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'category_new',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}

FEATURE_LIST_1 = [
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_1'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_2'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_3'
    },
]

FEATURE = {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_new'
    }

SUBCATEGORY = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'subcategory_name',
    'icon': None,
    'is_active': True
}


class TestSignalAddFeatureSubcategory(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        category = Category.objects.create(**CATEGORY)

        features = [Feature(**feature) for feature in FEATURE_LIST_1]
        Feature.objects.bulk_create(features)

        feature_category = [CategoryFeature(category_fk=category, feature_fk=feature)
                            for feature in features]
        CategoryFeature.objects.bulk_create(feature_category)

    def setUp(self):
        self.category = Category.objects.first()
        self.subcategory = Category(parent=self.category, **SUBCATEGORY)
        self.subcategory.save()

    def test_add_subcategory(self) -> None:
        """Проверка добавления характеристик в подкатегорию от родителя"""
        self.assertQuerysetEqual(Feature.objects.filter(categories=self.subcategory).order_by('id'),
                                 Feature.objects.filter(categories=self.category).order_by('id'))

    def test_update_feature_category(self) -> None:
        """Проверка изменения характеристики в подкатегории при изменении характеристик у родителя """
        feature = Feature.objects.create(**FEATURE)
        self.category.features.add(feature)
        self.category.save()

        self.assertQuerysetEqual(Feature.objects.filter(categories=self.subcategory).order_by('id'),
                                 Feature.objects.filter(categories=self.category).order_by('id'))

        self.category.features.remove(feature)
        self.category.save()

        self.assertQuerysetEqual(Feature.objects.filter(categories=self.subcategory).order_by('id'),
                                 Feature.objects.filter(categories=self.category).order_by('id'))

    def test_update_parent_category(self) -> None:
        """Проверка изменения характеристик в подкатегории при изменении ссылки на родителя"""
        category_new = Category.objects.create(**CATEGORY_NEW)
        feature = Feature.objects.create(**FEATURE)
        category_new.features.add(feature)
        category_new.save()

        self.subcategory.parent = category_new
        self.subcategory.save()

        self.assertQuerysetEqual(Feature.objects.filter(categories=self.subcategory).order_by('id'),
                                 Feature.objects.filter(categories=category_new).order_by('id'))

    def test_add_feature_to_subcategory(self) -> None:
        """Проверка добавления характеристик у подкатегории"""
        self.subcategory.features.create(**FEATURE)
        feature_new = Feature.objects.get(feature_id=FEATURE.get('feature_id'))

        self.assertIn(feature_new, Feature.objects.filter(categories=self.subcategory))
        self.assertNotIn(feature_new, Feature.objects.filter(categories=self.category))
