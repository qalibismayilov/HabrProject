
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_blocked",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_blocked",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = ("username",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Project permissions",
            {
                "fields": (
                    "role",
                    "is_blocked",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Project permissions",
            {
                "fields": (
                    "role",
                    "is_blocked",
                )
            },
        ),
    )
