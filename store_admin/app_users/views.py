from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView

from django.utils.translation import gettext as _

from app_users.forms import RegisterForm, ProfileRegisterForm
from app_users.models import Profile


class RegisterView(CreateView):
    model = User
    template_name = 'app_users/register.html'
    form_class = RegisterForm
    profile_form = ProfileRegisterForm
    success_url = '/users/register/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            user = form.save(commit=False)
            profile = Profile(user_fk=user)
            profile_form = self.profile_form(self.request.POST,
                                             instance=profile)
            if profile_form.is_valid():
                result = self.form_valid(form)
                profile_form.save()
                messages.success(self.request, _('Registration successful'))
                return result
        messages.error(request, _('Please correct the error'))
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.request.method == 'POST':
            profile_form = self.profile_form(self.request.POST,
                                             instance=self.object)
        else:
            profile_form = self.profile_form()
        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update({'profile_form': profile_form})
        return context


class UserLoginView(LoginView):
    template_name = 'app_users/login.html'


class UserLogoutView(LogoutView):
    next_page = '/'
