from django.contrib import admin

from .models import Collaboration, CollaborationFile, CollaborationTaskTag, CollaborationElement

admin.site.register(Collaboration)
admin.site.register(CollaborationFile)
admin.site.register(CollaborationTaskTag)
admin.site.register(CollaborationElement)
