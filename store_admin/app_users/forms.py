from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_users.models import Profile


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Profile with this Email already exists.'))
        return email


class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('tel_number', 'patronymic')
