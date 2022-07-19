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

DELIVERIES = {
    'Экспресс': 500,
    'Обычная': 100
}

DELIVERY_METHODS = {method: str(uuid.uuid4()) for method in DELIVERIES.keys()}
PAYMENT_METHODS = {method: str(uuid.uuid4()) for method in ['Счет', 'Карта']}

ORDERS_COUNT = 100

PAGE_SIZE = 50

now = datetime.utcnow()

# Установим соединение с БД используя контекстный менеджер with.
# В конце блока автоматически закроется курсор (cursor.close())
# и соединение (conn.close())
with psycopg2.connect(**dsn) as conn, conn.cursor() as cur:
    # todo: подумать может вынести заполнение таблиц в отельные функции/классы
    # Заполнение таблицы delivery_method
    query = 'INSERT INTO delivery_method (id, method_id, name, price, free_from) VALUES (%s, %s, %s, %s, %s)'
    data_delivery_methods = [
        (method_id, fake.uuid4(), name, DELIVERIES[name], random.randint(1000, 5000))
        for name, method_id in DELIVERY_METHODS.items()
    ]
    execute_batch(cur, query, data_delivery_methods, page_size=PAGE_SIZE)

    # Заполнение таблицы delivery
    query = 'INSERT INTO delivery (id, delivery_id, price, address, delivery_method_fk) VALUES (%s, %s, %s, %s, %s)'

    deliveries_ids = [str(uuid.uuid4()) for _ in range(ORDERS_COUNT)]
    data_deliveries = []

    for pk in deliveries_ids:
        delivery = random.choice(list(DELIVERIES.keys()))
        delivery_fk = DELIVERY_METHODS[delivery]
        price = DELIVERIES[delivery]
        data_deliveries.append((pk, fake.uuid4(), price, fake.address(), delivery_fk))

    execute_batch(cur, query, data_deliveries, page_size=PAGE_SIZE)

    # Заполнение таблицы payment_method
    query = 'INSERT INTO payment_method (id, method_id, name) VALUES (%s, %s, %s)'
    data_payment_methods = [
        (method_id, fake.uuid4(), name)
        for name, method_id in PAYMENT_METHODS.items()
    ]
    execute_batch(cur, query, data_payment_methods, page_size=PAGE_SIZE)

    # Заполнение таблицы payment
    query = 'INSERT INTO payment (id, payment_id, status_payment, error, payment_method_fk) ' \
            'VALUES (%s, %s, %s, %s, %s)'

    payments_ids = [str(uuid.uuid4()) for _ in range(ORDERS_COUNT)]

    data_payments = [
        (pk, fake.uuid4(), random.choice([True, False]),
         fake.sentence(nb_words=3), random.choice(list(PAYMENT_METHODS.values())))
        for pk in payments_ids
    ]
    execute_batch(cur, query, data_payments, page_size=PAGE_SIZE)

    # Заполнение таблицы order
    query = 'INSERT INTO "order" (id, order_id, created, total_price, username, delivery_fk, payment_fk) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s)'

    orders_ids = [str(uuid.uuid4()) for _ in range(ORDERS_COUNT)]

    data_orders = [
        (pk, fake.uuid4(), fake.date_time(), random.uniform(1_000, 10_000),
         fake.simple_profile()['username'], deliveries_ids[idx], payments_ids[idx])
        for idx, pk in enumerate(orders_ids)
    ]
    execute_batch(cur, query, data_orders, page_size=PAGE_SIZE)

    # Заполнение таблицы order_product
    query_product_ids = 'SELECT id FROM product'
    cur.execute(query_product_ids)
    product_ids = list(cur)

    query = 'INSERT INTO order_product (order_fk, product_fk) VALUES (%s, %s)'
    # data_order_product = [
    #     (order_id, random.choice(product_ids))
    #     for order_id in orders_ids
    #     for _ in range(random.randint(1, 5))
    # ]
    data_order_product = []

    for order_id in orders_ids:
        for _ in range(random.randint(1, 5)):
            product_id = random.choice(product_ids)

            if (order_id, product_id) not in data_order_product:
                data_order_product.append((order_id, product_id))

    execute_batch(cur, query, data_order_product, page_size=PAGE_SIZE)

    conn.commit()
