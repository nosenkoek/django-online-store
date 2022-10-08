from django.contrib import admin
from app_users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name',
                    'last_name', 'email', 'tel_number')
    search_fields = ('username', 'first_name')
    list_filter = ('is_staff', 'is_active')
