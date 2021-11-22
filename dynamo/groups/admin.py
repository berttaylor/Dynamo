from django.contrib import admin

from .models import Group, GroupJoinRequest, GroupProfileImage


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ("name", "slug")
    ordering = ("created_at",)

    list_display = (
        "name",
        "slug",
        "created_by",
    )

    list_filter = ("created_at",)

    fieldsets = (
        ("Group details", {"fields": (("name", "slug"), "description")}),
        ("Users", {"fields": ("created_by", "admins", "members", "subscribers")}),
        (
            "Database",
            {
                "fields": (
                    ("created_at", "updated_at"),
                    "deleted_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "slug",
    )


@admin.register(GroupJoinRequest)
class GroupJoinRequestAdmin(admin.ModelAdmin):
    search_fields = ("user", "group")
    ordering = ("created_at",)

    list_display = (
        "created_at",
        "user",
        "group",
        "status",
    )

    list_filter = (
        "created_at",
        "status",
    )

    fieldsets = (
        ("Request details", {"fields": (("user", "group"), "status")}),
        ("Handling", {"fields": (("handled_by", "handled_date"),)}),
        (
            "Database",
            {
                "fields": (
                    ("created_at", "updated_at"),
                    "deleted_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )


@admin.register(GroupProfileImage)
class GroupProfileImageAdmin(admin.ModelAdmin):
    search_fields = ("alt_text",)
    ordering = ("created_at",)

    list_display = ("alt_text",)

    list_filter = ("created_at",)

    fieldsets = (
        (None, {"fields": (("user", "group"), "status")}),
        (
            "Database",
            {
                "fields": (
                    ("created_at", "updated_at"),
                    "deleted_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
