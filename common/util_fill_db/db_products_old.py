import random
import uuid

from datetime import datetime

import psycopg2
from faker import Faker
from psycopg2.extras import execute_batch

from common.util_fill_db.settings import MANUFACTURERS_COUNT, PAGE_SIZE, \
    PRODUCTS_IN_CATEGORY_COUNT, PRODUCTS_LIMITED_COUNT, IMAGE_LINKS, \
    FEATURES_VALUE, FEATURES_GROUP_TEXT, DSN

fake = Faker()
now = datetime.utcnow()

with psycopg2.connect(**DSN) as conn, conn.cursor() as cur:
    query = 'SELECT category_id FROM category WHERE level=1 ' \
            'ORDER BY category_id;'
    cur.execute(query)
    category_ids = [category_id[0] for category_id in cur]
    category_feature = {}

    for category_id in category_ids:
        query = 'SELECT feature_fk FROM category_feature ' \
                'WHERE category_fk = %s;'
        cur.execute(query, (category_id,))
        category_feature.update(
            {category_id: [feature_id[0] for feature_id in cur]}
        )

    query = "SELECT feature_id FROM feature " \
            "WHERE type_feature::text = 'checkbox';"
    cur.execute(query)
    feature_id_ckeckbox = [feature_id[0] for feature_id in cur]

    query = "SELECT feature_id, name FROM feature " \
            "WHERE type_feature::text = 'select';"
    cur.execute(query)

    feature_id_name_select = {feature[0]: feature[1] for feature in cur}

    # Заполнение таблицы Manufacturer
    manufacturers_ids = [str(uuid.uuid4()) for _ in range(MANUFACTURERS_COUNT)]
    query = 'INSERT INTO manufacturer (id, manufacturer_id, name, updated) ' \
            'VALUES (%s, %s, %s, %s)'
    data_manufacturers = [(fake.uuid4(), uk, fake.company(), now)
                          for uk in manufacturers_ids]
    execute_batch(cur, query, data_manufacturers, page_size=PAGE_SIZE)

    # Заполнение таблицы Product
    query = 'INSERT INTO product (id, product_id, name, slug, description,' \
            'price, main_image, added, updated, count, is_limited,' \
            'category_fk, manufacturer_fk) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    product_category = {}
    data_products = []
    counter = 0
    data_images = []

    for num, category_id in enumerate(category_ids):
        product_ids = [str(uuid.uuid4())
                       for _ in range(PRODUCTS_IN_CATEGORY_COUNT)]

        for product_num, product_id in enumerate(product_ids):
            product_category.update({product_id: category_id})

            is_limited = True if product_num <= PRODUCTS_LIMITED_COUNT \
                else False

            counter += 1

            data_products.append(
                (fake.uuid4(), product_id, fake.company(),
                 f'product-{counter}', fake.sentence(nb_words=20),
                 round(random.uniform(100, 10_000), 2), IMAGE_LINKS[num],
                 fake.date_time(), now, random.randint(0, 50),
                 is_limited, category_id, random.choice(manufacturers_ids))
            )

            data_images.extend([
                (fake.uuid4(), fake.uuid4(), IMAGE_LINKS[num], product_id)
                for _ in range(random.randint(1, 4))
            ])

    execute_batch(cur, query, data_products, page_size=PAGE_SIZE)

    # Заполнение таблицы Image
    query = 'INSERT INTO image (id, image_id, image, product_fk) ' \
            'VALUES (%s, %s, %s, %s)'

    execute_batch(cur, query, data_images, page_size=PAGE_SIZE)

    # Заполнение таблицы product_feature
    query_product_feature = 'INSERT INTO product_feature ' \
                            '(id, product_fk, feature_fk, value) ' \
                            'VALUES (%s, %s, %s, %s)'

    data_product_feature = []

    for product_id in product_category.keys():
        category_id = product_category.get(product_id)
        feature_list = category_feature.get(category_id)
        for feature_id in feature_list:
            if feature_id in feature_id_ckeckbox:
                data_product_feature.append(
                    (str(uuid.uuid4()), product_id, feature_id,
                     random.choice(['yes', 'no'])))
            elif feature_id in feature_id_name_select.keys():
                data_product_feature.append(
                    (str(uuid.uuid4()), product_id, feature_id,
                     random.choice(
                         FEATURES_VALUE.get(
                             feature_id_name_select[feature_id])
                     )))
            elif feature_id in FEATURES_GROUP_TEXT.keys():
                data_product_feature.append((
                    str(uuid.uuid4()),
                    product_id,
                    feature_id,
                    ', '.join(set(random.choices(
                        FEATURES_GROUP_TEXT.get(feature_id), k=3)
                    ))))
            else:
                data_product_feature.append(
                    (str(uuid.uuid4()), product_id, feature_id, fake.word()))

    execute_batch(cur, query_product_feature,
                  data_product_feature, page_size=PAGE_SIZE)
