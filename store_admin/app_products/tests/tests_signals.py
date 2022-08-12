from uuid import uuid4

from django.test import TestCase
from django.utils.translation import gettext as _
from django.db import connection

from app_categories.models import Category, Feature, CategoryFeature
from app_products.models import Product, Manufacturer, ProductFeature

CATEGORY_PARENT = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'parent_1',
    'slug': 'parent-1',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}

CATEGORIES = [
    {
        'id': str(uuid4()),
        'category_id': str(uuid4()),
        'name': 'category_1',
        'slug': 'category-1',
        'icon': None,
        'is_active': True,
        'parent_id': CATEGORY_PARENT.get('category_id'),
    },
    {
        'id': str(uuid4()),
        'category_id': str(uuid4()),
        'name': 'category_2',
        'slug': 'category-2',
        'icon': None,
        'is_active': True,
        'parent_id': CATEGORY_PARENT.get('category_id'),
    }
]

FEATURE_LIST = [
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
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_4'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_5'
    },
]

FEATURE_NEW = {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_new'
    }

MANUFACTURER = {
    'id': str(uuid4()),
    'manufacturer_id': str(uuid4()),
    'name': 'manufacturer'
}

PRODUCT = {
    'id': str(uuid4()),
    'product_id': str(uuid4()),
    'name': 'product_1',
    'description': 'text',
    'price': 10_000,
    'is_limited': True,
}


class TestSignalAddFeatureProduct(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        Category.objects.create(**CATEGORY_PARENT)
        category_1 = Category.objects.create(**CATEGORIES[0])
        category_2 = Category.objects.create(**CATEGORIES[1])

        features_1 = [Feature(**feature) for feature in FEATURE_LIST[:2]]
        features_2 = [Feature(**feature) for feature in FEATURE_LIST[3:]]
        Feature.objects.bulk_create(features_1)
        Feature.objects.bulk_create(features_2)

        feature_category_1 = [CategoryFeature(category_fk=category_1, feature_fk=feature)
                              for feature in features_1]
        CategoryFeature.objects.bulk_create(feature_category_1)
        feature_category_2 = [CategoryFeature(category_fk=category_2, feature_fk=feature)
                              for feature in features_2]
        CategoryFeature.objects.bulk_create(feature_category_2)

        Manufacturer.objects.create(**MANUFACTURER)

    def setUp(self) -> None:
        self.manufacturer = Manufacturer.objects.first()
        self.category_1 = Category.objects.get(category_id=CATEGORIES[0].get('category_id'))
        self.category_2 = Category.objects.get(category_id=CATEGORIES[1].get('category_id'))
        self.product = Product.objects.create(**PRODUCT,
                                              category_fk=self.category_1,
                                              manufacturer_fk=self.manufacturer)

    def test_add_product(self):
        """Проверка добавления товара"""
        self.assertQuerysetEqual(self.product.features.all().order_by('feature_id'),
                                 Feature.objects.filter(categories=self.category_1).order_by('feature_id'))

    def test_update_category_in_product(self):
        """Проверка изменения категории у товара"""
        self.product.category_fk = self.category_2
        self.product.save(update_fields=['category_fk'])

        self.assertQuerysetEqual(self.product.features.all().order_by('feature_id'),
                                 Feature.objects.filter(categories=self.category_2).order_by('feature_id'))

    def test_update_feature_in_product_when_update_category(self):
        feature_new = Feature.objects.create(**FEATURE_NEW)
        category_feature_new = CategoryFeature.objects.create(category_fk=self.category_1, feature_fk=feature_new)

        self.assertQuerysetEqual(self.product.features.all().order_by('feature_id'),
                                 Feature.objects.filter(categories=self.category_1).order_by('feature_id'))

        category_feature_new.delete()
        self.assertQuerysetEqual(self.product.features.all().order_by('feature_id'),
                                 Feature.objects.filter(categories=self.category_1).order_by('feature_id'))




