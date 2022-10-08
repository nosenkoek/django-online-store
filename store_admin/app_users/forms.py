from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_users.models import Profile, file_size_validator


class ProfileRegisterForm(forms.ModelForm):
    """Форма профиля для регистрации пользователя"""
    class Meta:
        model = Profile
        fields = ('tel_number', 'patronymic')


class RegisterForm(UserCreationForm):
    """ Основная форма для регистрации пользователя"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2')

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Profile with this Email already exists.'))
        return email


class MyRegisterForm(RegisterForm):
    profile_form = ProfileRegisterForm

    def is_valid(self):
        if not super(MyRegisterForm, self).is_valid():
            return False

        user = self.save(commit=False)
        profile = Profile(user_fk=user)
        profile_form = self.profile_form(self.request.POST, instance=profile)

        if profile_form.is_valid():
            self.profile_form_clean = profile_form
            return True
        return False


class AddFullNameFieldMixin():
    """Миксин для добавления поля ФИО"""
    def clean_full_name(self) -> str:
        """
        Метод проверки и преобразования ФИО
        :return: ФИО
        """
        full_name = self.cleaned_data.pop('full_name')
        full_name_words = full_name.split()

        length_name = len(full_name_words)

        if length_name == 2:
            self.cleaned_data.update({
                'last_name': full_name_words[0],
                'first_name': full_name_words[1]
            })
        elif length_name == 3:
            self.cleaned_data.update({
                'last_name': full_name_words[0],
                'first_name': full_name_words[1],
                'patronymic': full_name_words[2]
            })
        else:
            raise ValidationError(_('Enter full name. First name, '
                                    'last name and patronymic'))
        return full_name


class AddPassportFieldMixin():
    """Миксин для добавления полей для ввода нового пароля"""
    def clean_password2(self) -> str:
        """
        Валидация введенных паролей.
        :return: пароль
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            password_validation.validate_password(password2, self.instance)
            if password1 != password2:
                raise ValidationError(
                    _('The two password fields didn’t match.'),
                    code='password_mismatch',
                )
        return password2


class UserProfileForm(forms.ModelForm, AddFullNameFieldMixin,
                      AddPassportFieldMixin):
    """Основная форма для редактирования профиля пользователя"""
    full_name = forms.CharField(
        label=_('Full name. Last name, first name, patronymic')
    )
    password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=False
    )
    password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if (email != self.instance.email and
                User.objects.filter(email=email).exists()):
            raise ValidationError(_('Profile with this Email already exists.'))
        return email


class ProfileForm(forms.ModelForm):
    """Дополнительная форма для редактирования профиля пользователя"""
    class Meta:
        model = Profile
        fields = ('tel_number', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        file_size_validator(avatar)
        return avatar
