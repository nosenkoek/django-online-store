DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', 5432),
        'OPTIONS': {
            'options': '-c search_path=public,content'
        }
    }
}

REDIS_HOST = 'redis'
REDIS_PORT = 6379

ES_HOST = 'es'
ES_PORT = 9200
