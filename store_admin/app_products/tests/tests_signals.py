from django.test import TestCase
from django.db import connection

from app_categories.models import Category, Feature, CategoryFeature
from app_products.models import Product, Manufacturer

from app_products.tests.settings import CATEGORY_PARENT, MANUFACTURER, PRODUCT, \
    CATEGORY_LIST, FEATURE_LIST, FEATURE_NEW


class TestSignalAddFeatureProduct(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        # todo: fixtures in test
        Category.objects.create(**CATEGORY_PARENT)
        category_1 = Category.objects.create(**CATEGORY_LIST[0])
        category_2 = Category.objects.create(**CATEGORY_LIST[1])

        features_1 = [Feature(**feature) for feature in FEATURE_LIST[:2]]
        features_2 = [Feature(**feature) for feature in FEATURE_LIST[3:]]
        Feature.objects.bulk_create(features_1)
        Feature.objects.bulk_create(features_2)

        feature_category_1 = [
            CategoryFeature(category_fk=category_1, feature_fk=feature)
            for feature in features_1]
        CategoryFeature.objects.bulk_create(feature_category_1)
        feature_category_2 = [
            CategoryFeature(category_fk=category_2, feature_fk=feature)
            for feature in features_2]
        CategoryFeature.objects.bulk_create(feature_category_2)

        Manufacturer.objects.create(**MANUFACTURER)

    def setUp(self) -> None:
        self.manufacturer = Manufacturer.objects.first()
        self.category_1 = Category.objects.get(
            category_id=CATEGORY_LIST[0].get('category_id'))
        self.category_2 = Category.objects.get(
            category_id=CATEGORY_LIST[1].get('category_id'))
        self.product = Product.objects.create(
            **PRODUCT,
            category_fk=self.category_1,
            manufacturer_fk=self.manufacturer
        )

    def test_add_product(self):
        """Проверка добавления товара"""
        self.assertQuerysetEqual(
            self.product.features.all().order_by('feature_id'),
            Feature.objects.filter(categories=self.category_1).order_by(
                'feature_id'))

    def test_update_category_in_product(self):
        """Проверка изменения категории у товара"""
        self.product.category_fk = self.category_2
        self.product.save(update_fields=['category_fk'])

        self.assertQuerysetEqual(
            self.product.features.all().order_by('feature_id'),
            Feature.objects.filter(categories=self.category_2)
            .order_by('feature_id'))

    def test_update_feature_in_product_when_update_category(self):
        feature_new = Feature.objects.create(**FEATURE_NEW)
        category_feature_new = CategoryFeature.objects.create(
            category_fk=self.category_1, feature_fk=feature_new)

        self.assertQuerysetEqual(
            self.product.features.all().order_by('feature_id'),
            Feature.objects.filter(categories=self.category_1).order_by(
                'feature_id'))

        category_feature_new.delete()
        self.assertQuerysetEqual(
            self.product.features.all().order_by('feature_id'),
            Feature.objects.filter(categories=self.category_1).order_by(
                'feature_id'))
