from django.contrib import admin

# Register your models here.
from chat.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    search_fields = ("user", "message", "group", "collaboration")
    ordering = ("created_at",)

    list_display = (
        "created_at",
        "user",
        "message",
        "group",
        "collaboration",
    )

    list_filter = (
        "created_at",
    )

    fieldsets = (
        (None, {"fields": (("group", "collaboration"), "user", "message")}),
        ("Database", {"fields": (("created_at", "updated_at"), "deleted_at",)}),
    )

    readonly_fields = ("created_at", "updated_at", "deleted_at",)