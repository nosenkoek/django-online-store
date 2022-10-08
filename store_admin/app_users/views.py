import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView

from django.utils.translation import gettext as _

from app_users.forms import RegisterForm, ProfileRegisterForm, \
    UserProfileForm, ProfileForm, MyRegisterForm
from app_users.models import Profile
from app_users.services.edit_profile_services import GetProfileFormMixin, \
    LoginUserMixin

logger = logging.getLogger(__name__)


class RegisterView(CreateView, LoginUserMixin):
    """View для регистрации пользователя"""
    model = User
    template_name = 'app_users/register.html'
    form_class = MyRegisterForm
    success_url = '/users/register/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.request = request

        if form.is_valid():
            result = self.form_valid(form)
            messages.success(self.request, _('Registration successful'))

            self.authenticate_and_login(form.cleaned_data.get('username'),
                                        form.cleaned_data.get('password1'))

            return result
        messages.error(request, _('Please correct the error'))
        return self.form_invalid(form)

    def form_valid(self, form):
        result = super(RegisterView, self).form_valid(form)
        form.profile_form_clean.save()
        return result

    def get_context_data(self, **kwargs):
        if self.request.method == 'POST':
            profile_form = self.form_class.profile_form(self.request.POST,
                                                        instance=self.object)
        else:
            profile_form = self.form_class.profile_form()
        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update({'profile_form': profile_form})
        return context


class UserLoginView(LoginView):
    """View для входа пользователя"""
    template_name = 'app_users/login.html'

    def post(self, request, *args, **kwargs):
        result = super(UserLoginView, self).post(request, *args, **kwargs)
        logger.info(f'Login user | {self.request.user.username}')
        return result


class UserLogoutView(LogoutView):
    """View для выхода пользователя"""
    next_page = '/'


class AccountView(LoginRequiredMixin, DetailView):
    """View для страницы профиля"""
    login_url = '/users/login/'
    template_name = 'app_users/account.html'
    model = User
    context_object_name = 'user'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj


class ProfileView(LoginRequiredMixin, UpdateView, GetProfileFormMixin,
                  LoginUserMixin):
    """View для страницы редактирования профиля"""
    login_url = '/users/login/'
    model = User
    template_name = 'app_users/profile.html'
    form_class = UserProfileForm
    profile_form = ProfileForm
    success_url = '/users/profile/'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        profile_form = self.get_profile_form()

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile = profile_form.save(commit=False)
            profile.patronymic = form.cleaned_data.get('patronymic')
            profile.save()

            password = form.cleaned_data.get('password2')
            if password:
                raw_password = self.object.set_password(password)
                username = self.object.username
                self.authenticate_and_login(username, raw_password)

            messages.success(self.request,
                             _('Edit profile successful'))
            logger.info(f'Profile Edit | {self.object.username}')
            return self.form_valid(form)
        messages.error(request, _('Please correct the error'))
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({'profile_form': self.get_profile_form()})
        return context
