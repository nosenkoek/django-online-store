DSN = {
    'dbname': 'store_db',
    'user': 'admin',
    'password': 'admin',
    'host': 'db',
    'port': 5432,
    'options': '-c search_path=content',
    'connect_timeout': 5
}

REDIS_HOST = 'redis'
REDIS_PORT = 6379

ES_HOST = 'es'
ES_PORT = 9200

COUNT_ROW_IN_PACKAGE = 100
ES_FIELDS = ['product_id', 'category', 'name', 'description', 'manufacturer']
