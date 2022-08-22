from uuid import uuid4

COUNT_PRODUCT_IN_PAGE = 8

PRODUCT = {
    'id': str(uuid4()),
    'product_id': str(uuid4()),
    'name': 'product_1',
    'description': 'text',
    'price': 10_000,
    'is_limited': True,
    'count': 10,
}

MANUFACTURER = {
    'id': str(uuid4()),
    'manufacturer_id': str(uuid4()),
    'name': 'manufacturer'
}

CATEGORY_PARENT = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'parent_1',
    'slug': 'parent-1',
    'icon': None,
    'is_active': True,
    'parent_id': None,
}

CATEGORY = {
    'id': str(uuid4()),
    'category_id': str(uuid4()),
    'name': 'category_2',
    'slug': 'category-2',
    'icon': None,
    'is_active': True,
    'parent_id': CATEGORY_PARENT.get('category_id'),
}

CATEGORY_LIST = [
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
        'name': 'feature_1',
        'slug': 'feature_1',
        'type_feature': 'text'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_2',
        'slug': 'feature_2',
        'type_feature': 'select'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_3',
        'slug': 'feature_3',
        'type_feature': 'checkbox'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_4',
        'slug': 'feature_4',
        'type_feature': 'text'
    },
    {
        'id': str(uuid4()),
        'feature_id': str(uuid4()),
        'name': 'feature_5',
        'slug': 'feature_5',
        'type_feature': 'select'
    },
]

FEATURE_NEW = {
    'id': str(uuid4()),
    'feature_id': str(uuid4()),
    'name': 'feature_new',
    'slug': 'feature_new',
}