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
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432,
    'options': '-c search_path=content',
}

MANUFACTURERS_COUNT = 5
PRODUCTS_COUNT = 2_000
PRODUCTS_LIMITED_COUNT = 16
PAGE_SIZE = 50

now = datetime.utcnow()

# Установим соединение с БД используя контекстный менеджер with.
# В конце блока автоматически закроется курсор (cursor.close())
# и соединение (conn.close())
with psycopg2.connect(**dsn) as conn, conn.cursor() as cur:
    query = 'SELECT category_id FROM category;'
    cur.execute(query)
    category_ids = [category_id[0] for category_id in cur]
    category_feature = {}

    for category_id in category_ids:
        query = 'SELECT feature_fk FROM category_feature WHERE category_fk = %s;'
        cur.execute(query, (category_id,))
        category_feature.update({category_id: [feature_id[0] for feature_id in cur]})

    query = "SELECT feature_id FROM feature WHERE type_feature::text = 'checkbox';"
    cur.execute(query)
    feature_id_ckeckbox = [feature_id[0] for feature_id in cur]

    # Заполнение таблицы Manufacturer
    manufacturers_ids = [str(uuid.uuid4()) for _ in range(MANUFACTURERS_COUNT)]
    query = 'INSERT INTO manufacturer (id, manufacturer_id, name) VALUES (%s, %s, %s)'
    data_manufacturers = [(fake.uuid4(), uk, fake.company())
                          for uk in manufacturers_ids]
    execute_batch(cur, query, data_manufacturers, page_size=PAGE_SIZE)

    # Заполнение таблицы Product
    query = 'INSERT INTO product (id, product_id, name, description, price, ' \
            'image, added, is_limited,' \
            'category_fk, manufacturer_fk) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    product_ids = [str(uuid.uuid4()) for _ in range(PRODUCTS_COUNT)]
    product_category = {}
    data_products = []

    for product_id in product_ids:
        category_current = random.choice(category_ids)
        product_category.update({product_id: category_current})

        data_products.append(
            (fake.uuid4(), product_id, fake.company(), fake.sentence(nb_words=10),
             round(random.uniform(1, 1_000), 2), fake.word(), fake.date_time(),
             False, category_current, random.choice(manufacturers_ids))
        )

    execute_batch(cur, query, data_products, page_size=PAGE_SIZE)

    query_update_is_limited = "UPDATE product SET is_limited = %s WHERE product_id = %s"
    data_update_is_limited = [(True, random.choice(product_ids)) for _ in range(PRODUCTS_LIMITED_COUNT)]
    execute_batch(cur, query_update_is_limited, data_update_is_limited, page_size=PAGE_SIZE)

    # Заполнение таблицы product_feature
    query_product_feature = 'INSERT INTO product_feature (id, product_fk, feature_fk, value) VALUES (%s, %s, %s, %s)'

    data_product_feature = []

    for product_id in product_ids:
        category_id = product_category.get(product_id)
        feature_list = category_feature.get(category_id)
        for feature_id in feature_list:
            if feature_id in feature_id_ckeckbox:
                data_product_feature.append((str(uuid.uuid4()), product_id, feature_id, random.choice(['yes', 'no'])))
            else:
                data_product_feature.append((str(uuid.uuid4()), product_id, feature_id, fake.word()))

    execute_batch(cur, query_product_feature, data_product_feature, page_size=PAGE_SIZE)
