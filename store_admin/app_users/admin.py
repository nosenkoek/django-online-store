from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from app_users.models import Profile, Feedback
from app_users.filters import FeedbackProductFilterAdmin, \
    FeedbackUsernameFilterAdmin

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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'user', 'product')
    search_fields = ('text', )
    list_filter = (FeedbackUsernameFilterAdmin, FeedbackProductFilterAdmin)

    @admin.display(description=_('text'))
    def short_text(self, obj) -> str:
        """Отображение текста отзыва"""
        return obj.text[:15]

    @admin.display(description=_('user'))
    def user(self, obj) -> str:
        """Доп. поле отображения пользователя"""
        return obj.user_fk.username

    @admin.display(description=_('product'))
    def product(self, obj) -> str:
        """Доп. поле отображения товара"""
        return obj.product_fk.name
