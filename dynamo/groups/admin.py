from django.contrib import admin

from .models import Group, GroupJoinRequest, GroupProfileImage

admin.site.register(Group)
admin.site.register(GroupJoinRequest)
admin.site.register(GroupProfileImage)

