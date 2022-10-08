import logging

from django.forms import Form
from django.contrib.auth import authenticate, login

logger = logging.getLogger(__name__)


class GetProfileFormMixin():
    """Миксин для отображения изменения профиля"""
    def get_profile_form(self) -> Form:
        """
        Возвращает объект формы профиля исходя из запроса.
        :return: объект формы профиля
        """
        user = self.get_object()
        initial_dict = {
            'tel_number': user.profile.tel_number,
            'avatar': user.profile.avatar,
        }
        if self.request.method == 'POST':
            profile_form = self.profile_form(self.request.POST,
                                             instance=user.profile,
                                             files=self.request.FILES,
                                             initial=initial_dict)
        else:
            profile_form = self.profile_form(instance=user.profile)
        return profile_form


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
