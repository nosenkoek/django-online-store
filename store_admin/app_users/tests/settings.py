import os

from django.conf import settings

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_media')


USERNAME = 'usertest'
PASSWORD = 'test12345'

DATA_USER = {
    'username': 'user12345',
    'first_name': 'test',
    'last_name': 'test',
    'email': 'test@test.ru',
    'password1': 'lala45678',
    'password2': 'lala45678',
    'patronymic': 'patronymic',
    'tel_number': '0123456789'
}

DATA_EDIT_PROFILE = {
    'full_name': 'test_new test_new patronymic_new',
    'email': 'test_new@test.ru',
    'password1': 'lala45678_new',
    'password2': 'lala45678_new',
    'tel_number': '0000000000'
}