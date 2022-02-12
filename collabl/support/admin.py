from django.contrib import admin

from .models import FAQ, FAQCategory, SupportMessage


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    ordering = (
        "category",
        "position",
    )

    list_display = (
        "question",
        "answer",
        "category",
        "position",
    )

    list_filter = (
        "category",
        "created_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "question",
                    "answer",
                )
            },
        ),
        ("Position", {"fields": (("category", "position"),)}),
        ("Database", {"fields": (("created_at", "updated_at"),)}),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    ordering = ("name",)

    list_display = ("name",)

    list_filter = ("created_at",)

    fieldsets = (
        (
            None,
            {"fields": ("name",)},
        ),
        ("Database", {"fields": (("created_at", "updated_at"),)}),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    ordering = (
        "-read",
        "created_at",
    )

    list_display = (
        "created_at",
        "email",
        "read",
    )

    list_filter = (
        "read",
        "created_at",
    )

    fieldsets = (
        ("User", {"fields": (("name", "email"), "related_user_account")}),
        ("Handling", {"fields": ("read",)}),
        (
            "Message",
            {"fields": ("message",)},
        ),
        ("Database", {"fields": (("created_at", "updated_at"),)}),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "name",
        "email",
        "message",
    )

    # Support Messages are created by users on the front end.
    def has_add_permission(self, request):
        return False
