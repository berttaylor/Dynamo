from django.contrib import admin

from .models import Group, GroupJoinRequest

admin.site.register(Group)
admin.site.register(GroupJoinRequest)

