from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import UserRegisterForm
from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm
    list_display = ("id", "email", "phone_number", "country", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("first_name", "last_name", "avatar", "phone_number", "country")},
        ),
        (
            "Права доступа",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
