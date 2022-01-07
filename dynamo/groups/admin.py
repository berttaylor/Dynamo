from django.contrib import admin

from .models import Group, GroupProfileImage, GroupAnnouncement, Membership


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
        ("Users", {"fields": ("created_by",)}),
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


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
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
        ("Membership details", {"fields": (("user", "group"), "status", 'is_subscribed')}),
        ("Handling", {"fields": ("updated_by",)}),
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


@admin.register(GroupAnnouncement)
class GroupAnnouncementAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    ordering = ("created_at",)

    list_display = (
        "title",
        "group",
    )

    list_filter = ("created_at",)

    fieldsets = (
        (None, {"fields": (("user", "group"),)}),
        (
            "Announcement",
            {
                "fields": (
                    "title",
                    "body",
                )
            },
        ),
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
