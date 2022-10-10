import logging
from typing import Dict

from django.contrib.auth import authenticate, login

from app_users.forms import UserProfileForm
from app_users.models import User

logger = logging.getLogger(__name__)


class LoginUserMixin():
    """Миксин для принудительного входа пользователя"""
    def authenticate_and_login(self, username: str, raw_password: str) -> None:
        """
        Вход в систему пользователя
        :param username: логин
        :param raw_password: пароль
        """
        user = authenticate(username=username,
                            password=raw_password)
        login(self.request, user)
        logger.info(f'New user | {username}')


class InitialDictMixin():
    """Миксин для заполнения initial"""
    @staticmethod
    def get_initial_form(user: User) -> Dict[str, str]:
        """
        Создание словаря для заполнения формы из БД
        :param user: объект пользователя,
        :return: словарь с данными из БД
        """
        initial_dict = {
            'full_name': user.get_full_name(),
            'avatar': user.avatar,
            'email': user.email,
            'tel_number': user.tel_number,
        }
        return initial_dict


class SetPasswordMixin():
    """Установка нового пароля и вход в систему"""
    def set_password(self, form: UserProfileForm) -> None:
        password = form.cleaned_data.get('password2')
        if password:
            raw_password = self.object.set_password(password)
            username = self.object.username
            self.authenticate_and_login(username, raw_password)
