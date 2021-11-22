from django.contrib import admin

from .models import (
    Collaboration,
    CollaborationFile,
    CollaborationMilestone,
    CollaborationTask,
    CollaborationTaskTag,
)


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    search_fields = ("name", "related_group")
    ordering = ("created_at",)

    list_display = (
        "name",
        "slug",
        "related_group",
    )

    list_filter = ("created_at", "related_group")

    fieldsets = (
        ("Collaboration details", {"fields": (("name", "slug"), "description")}),
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


@admin.register(CollaborationTask)
class CollaborationTaskAdmin(admin.ModelAdmin):
    search_fields = ("reference", "name", "collaboration")
    ordering = ("collaboration", "position")

    list_display = (
        "reference",
        "name",
        "collaboration",
        "position",
    )

    list_filter = (
        "created_at",
        "collaboration",
    )

    fieldsets = (
        (
            "Task details",
            {
                "fields": (
                    ("reference", "collaboration"),
                    ("name", "description"),
                    "assigned_to",
                    "prerequisites",
                    "position",
                )
            },
        ),
        (
            "Completion",
            {"fields": (("completed_at", "completed_by"), "completion_notes")},
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
        "reference",
        "prerequisites",
    )


@admin.register(CollaborationMilestone)
class CollaborationMilestoneAdmin(admin.ModelAdmin):
    search_fields = ("reference", "name", "collaboration")
    ordering = ("collaboration", "position")

    list_display = (
        "reference",
        "name",
        "collaboration",
        "position",
    )

    list_filter = (
        "created_at",
        "collaboration",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("reference", "collaboration"),
                    ("name", "target_date"),
                    "prerequisites",
                    "position",
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
        "reference",
        "prerequisites",
    )


@admin.register(CollaborationTaskTag)
class CollaborationTaskTagAdmin(admin.ModelAdmin):
    ordering = ("name",)

    list_display = ("name",)

    list_filter = ("created_at",)

    fieldsets = (
        (None, {"fields": ("name",)}),
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


@admin.register(CollaborationFile)
class CollaborationFileAdmin(admin.ModelAdmin):
    ordering = ("name",)
    search_fields = ("name",)

    list_display = (
        "created_at",
        "name",
        "collaboration",
        "format",
    )

    list_filter = ("format",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "collaboration",
                    ("name", "format"),
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
