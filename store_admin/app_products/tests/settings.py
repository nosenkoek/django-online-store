import os

from uuid import uuid4

from django.conf import settings

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_media/')

COUNT_PRODUCT_IN_PAGE = 8

NUMBERS_PRODUCT = 20

PRICE_FROM = 10
PRICE_TO = 5_000

PRODUCT = {
    'id': str(uuid4()),
    'product_id': str(uuid4()),
    'name': 'product_1',
    'description': 'text',
    'price': 10_000,
    'is_limited': True,
    'count': 10,
}

FEATURE_NEW = {
    'id': str(uuid4()),
    'feature_id': str(uuid4()),
    'name': 'feature_new',
    'slug': 'feature_new',
}
