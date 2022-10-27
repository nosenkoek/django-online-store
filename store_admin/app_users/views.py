import logging
from typing import Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.views.generic import CreateView, DetailView, UpdateView
from django.utils.translation import gettext as _

from app_cart.services.mixins_for_cart import GetContextTotalPriceCartMixin
from app_categories.services.navi_categories_list import NaviCategoriesList
from app_users.forms import RegisterForm, UserProfileForm
from app_users.models import User
from app_users.services.services_views import LoginUserMixin, \
    InitialDictMixin, SetPasswordMixin

logger = logging.getLogger(__name__)


class RegisterView(CreateView, LoginUserMixin, GetContextTotalPriceCartMixin):
    """View для регистрации пользователя"""
    model = User
    template_name = 'app_users/register.html'
    form_class = RegisterForm
    success_url = '/users/register/'

    def form_valid(self, form) -> HttpResponse:
        result = super(RegisterView, self).form_valid(form)
        messages.success(self.request, _('Registration successful'))
        self.authenticate_and_login(form.cleaned_data.get('username'),
                                    form.cleaned_data.get('password1'))
        return result

    def form_invalid(self, form) -> HttpResponse:
        result = super(RegisterView, self).form_invalid(form)
        messages.error(self.request, _('Please correct the error'))
        return result

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context


class UserLoginView(LoginView, GetContextTotalPriceCartMixin):
    """View для входа пользователя"""
    template_name = 'app_users/login.html'

    def post(self, request, *args, **kwargs):
        result = super(UserLoginView, self).post(request, *args, **kwargs)
        logger.info(f'Login user | {self.request.user.username}')
        return result

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(UserLoginView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context


class UserLogoutView(LogoutView):
    """View для выхода пользователя"""
    next_page = '/'


class AccountView(LoginRequiredMixin, DetailView,
                  GetContextTotalPriceCartMixin):
    """View для страницы профиля"""
    login_url = '/users/login/'
    template_name = 'app_users/account.html'
    model = settings.AUTH_USER_MODEL
    context_object_name = 'user'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(AccountView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context


class ProfileView(LoginRequiredMixin, UpdateView,
                  InitialDictMixin, LoginUserMixin, SetPasswordMixin,
                  GetContextTotalPriceCartMixin):
    """View для страницы редактирования профиля"""
    login_url = '/users/login/'
    model = User
    template_name = 'app_users/profile.html'
    form_class = UserProfileForm
    success_url = '/users/profile/'
    context_object_name = 'user'

    def get_initial(self):
        self.initial = self.get_initial_form(self.request.user)
        return self.initial

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form) -> HttpResponse:
        self.set_password(form)
        result = super(ProfileView, self).form_valid(form)
        messages.success(self.request, _('Registration successful'))
        return result

    def form_invalid(self, form) -> HttpResponse:
        result = super(ProfileView, self).form_invalid(form)
        messages.error(self.request, _('Please correct the error'))
        return result

    def get_context_data(self, **kwargs) -> Dict[str, str]:
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update(NaviCategoriesList().get_context())
        context.update(self.get_context_price_cart())
        return context
