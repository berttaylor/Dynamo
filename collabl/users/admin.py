from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("email", "first_name")
    ordering = ("email",)

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "date_joined",
        "last_login",
        "is_staff",
        "is_active",
        "is_superuser",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                )
            },
        ),
        (
            "Image",
            {"fields": ("image",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                )
            },
        ),
        (
            "Database information",
            {"fields": (("date_joined", "last_login"),)},
        ),
    )

    readonly_fields = (
        "password",
        "date_joined",
        "last_login",
    )

    # Users are added through registering on the site, or using the createsuperuser command (for devs/admins)
    def has_add_permission(self, request):
        return False
