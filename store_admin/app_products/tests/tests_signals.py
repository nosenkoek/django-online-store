import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.db import connection

from app_categories.models import Category, Feature, CategoryFeature
from app_products.models import Product, Manufacturer

from app_products.tests.settings import PRODUCT, FEATURE_NEW, TEMP_MEDIA_ROOT


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestSignalAddFeatureProduct(TestCase):
    fixtures = \
        ['app_products/tests/fixtures/fixtures_test_product_signal.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        SimpleUploadedFile(name='small_1.gif',
                           content=(b'\x47\x49\x46\x38\x39\x61\x02\x00'
                                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                                    b'\x0A\x00\x3B'),
                           content_type='image/gif')

        super(TestSignalAddFeatureProduct, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.manufacturer = Manufacturer.objects.first()
        self.category_1 = Category.objects.get(slug='subcategory_1')
        self.category_2 = Category.objects.get(slug='subcategory_2')

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
