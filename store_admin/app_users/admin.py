from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from app_users.models import Profile

admin.site.unregister(User)


class UserInLine(admin.StackedInline):
    model = Profile
    verbose_name = 'Профиль'
    verbose_name_plural = 'Дополнительная информация'


class ListDisplayUserExtendMixin():
    """Миксин для расширения list_display"""
    list_select_related = ('profile', )
    list_display = ('username', 'first_name', 'last_name',
                    'patronymic', 'tel_number', 'email',
                    'is_staff', 'is_active')

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request)\
            .select_related(*self.list_select_related)
        return queryset

    @admin.display(description=_('patronymic'))
    def patronymic(self, obj) -> str:
        """Доп. поле отображения отчества"""
        return obj.profile.patronymic

    @admin.display(description=_('tel_number'))
    def tel_number(self, obj) -> str:
        """Доп. поле отображения отчества"""
        return obj.profile.tel_number


@admin.register(User)
class UserAdmin(ListDisplayUserExtendMixin, admin.ModelAdmin):
    inlines = (UserInLine,)
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
