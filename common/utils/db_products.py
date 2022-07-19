import random
import uuid
import psycopg2

from datetime import datetime
from faker import Faker
from psycopg2.extras import execute_batch

fake = Faker()

# Подготавливаем DSN (Data Source Name) для подключения к БД Postgres
dsn = {
    'dbname': 'store_db',
    'user': 'app',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432,
    'options': '-c search_path=content',
}

CATEGORIES_FEATURES = {
    'Холодильники': ['Вес', 'Габариты'],
    'Телефоны': ['Вес', 'Габариты', 'Память', 'Экран'],
    'Ноутбуки': ['Вес', 'Габариты', 'Память', 'Экран']
}

CATEGORIES = {item: str(uuid.uuid4()) for item in CATEGORIES_FEATURES.keys()}
FEATURES = {item: str(uuid.uuid4()) for item in ['Вес', 'Габариты', 'Память', 'Экран']}

FEEDBACKS_COUNT = 20
MANUFACTURERS_COUNT = 5
PRODUCTS_COUNT = 20

PAGE_SIZE = 50

now = datetime.utcnow()

# Установим соединение с БД используя контекстный менеджер with.
# В конце блока автоматически закроется курсор (cursor.close())
# и соединение (conn.close())
with psycopg2.connect(**dsn) as conn, conn.cursor() as cur:
    # todo: подумать может вынести заполнение таблиц в отельные функции/классы
    # # Заполнение таблицы category
    query = 'INSERT INTO category (id, category_id, name, is_active) VALUES (%s, %s, %s, %s)'
    data_categories = [(category_id, fake.uuid4(), name, random.choice([True, False]))
                       for name, category_id in CATEGORIES.items()]
    execute_batch(cur, query, data_categories, page_size=PAGE_SIZE)

    # # Заполнение таблицы feature
    query = 'INSERT INTO feature (id, feature_id, name) VALUES (%s, %s, %s)'
    data_features = [(feature_id, fake.uuid4(), name)
                     for name, feature_id, in FEATURES.items()]
    execute_batch(cur, query, data_features, page_size=PAGE_SIZE)

    # # Заполнение таблицы category_feature
    query = 'INSERT INTO category_feature (category_fk, feature_fk) VALUES (%s, %s)'

    data_category_feature = [(CATEGORIES[category], FEATURES[feature])
                             for category, feature_list in CATEGORIES_FEATURES.items()
                             for feature in feature_list]

    execute_batch(cur, query, data_category_feature, page_size=PAGE_SIZE)

    # Заполнение таблицы Feedback
    feedbacks_ids = [str(uuid.uuid4()) for _ in range(FEEDBACKS_COUNT)]
    query = 'INSERT INTO feedback (id, feedback_id, text, username) VALUES (%s, %s, %s, %s)'
    data_feedbacks = [(pk, fake.uuid4(), fake.sentence(nb_words=10), fake.simple_profile()['username'])
                      for pk in feedbacks_ids]
    execute_batch(cur, query, data_feedbacks, page_size=PAGE_SIZE)

    # Заполнение таблицы Manufacturer
    manufacturers_ids = [str(uuid.uuid4()) for _ in range(MANUFACTURERS_COUNT)]
    query = 'INSERT INTO manufacturer (id, manufacturer_id, name) VALUES (%s, %s, %s)'
    data_manufacturers = [(pk, fake.uuid4(), fake.company())
                          for pk in manufacturers_ids]
    execute_batch(cur, query, data_manufacturers, page_size=PAGE_SIZE)

    # Заполнение таблицы Product
    product_ids = [str(uuid.uuid4()) for _ in range(PRODUCTS_COUNT)]
    query = 'INSERT INTO product (id, product_id, name, description, price, ' \
            'image, added, is_limited,' \
            'category_fk, manufacturer_fk, feedback_fk) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    data_products = [
        (pk, fake.uuid4(), fake.company(), fake.sentence(nb_words=10), random.uniform(1, 1_000),
         fake.word(), fake.date_time(), random.choice([True, False]),
         random.choice(list(CATEGORIES.values())), random.choice(manufacturers_ids), random.choice(feedbacks_ids))
        for pk in product_ids
    ]
    execute_batch(cur, query, data_products, page_size=PAGE_SIZE)

    # Заполнение таблицы product_feature
    query_product_feature = 'INSERT INTO product_feature (product_fk, feature_fk, value) VALUES (%s, %s, %s)'

    data_product_feature = []

    for product_id in product_ids:
        query = 'SELECT cf.feature_fk ' \
                'FROM category_feature cf ' \
                'JOIN product p ON cf.category_fk = p.category_fk AND p.id::text = %s;'
        cur.execute(query, (product_id,))

        for feature in cur:
            data_product_feature.append((product_id, feature, fake.word()))

    execute_batch(cur, query_product_feature, data_product_feature, page_size=PAGE_SIZE)
    conn.commit()
