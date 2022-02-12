from django.contrib import admin

from .models import (
    Collaboration,
    CollaborationMilestone,
    CollaborationTask,
)

"""
Inlines
"""


class CollaborationTaskInline(admin.TabularInline):
    model = CollaborationTask
    extra = 0
    fields = (
        "reference",
        "name",
        "position",
        "assigned_to",
        "completed_at",
        "completed_by",
    )


class CollaborationMilestoneInline(admin.TabularInline):
    model = CollaborationMilestone
    extra = 0


"""
Admin Classes
"""


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    search_fields = ("name", "related_group")
    ordering = ("created_at",)

    list_display = (
        "name",
        "slug",
        "related_group",
        "number_of_tasks",
        "number_of_tasks_completed",
    )

    list_filter = ("created_at", "related_group")

    fieldsets = (
        (
            "Collaboration details",
            {"fields": (("name", "slug"), "description", "image", "related_group")},
        ),
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

    inlines = [CollaborationTaskInline, CollaborationMilestoneInline]

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
            {
                "fields": (
                    ("completed_at", "completed_by"),
                    "completion_notes",
                    "file",
                    "prompt_for_details_on_completion",
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
