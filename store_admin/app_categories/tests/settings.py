import os

from uuid import uuid4

from django.conf import settings

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_media/')

NUMBERS_CATEGORY = 6
NUMBERS_RANDOM_CATEGORY = 3
NUMBERS_POPULAR_PRODUCTS = 8
NUMBERS_LIMIT_PRODUCTS = 16

FEATURE = {
    'id': str(uuid4()),
    'feature_id': str(uuid4()),
    'name': 'feature_name',
    'slug': 'slug',
    'type_feature': 'text'
}

CATEGORY = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'category_name',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}
