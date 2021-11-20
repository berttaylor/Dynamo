from django.contrib import admin

from .models import FAQ, FAQCategory, SupportMessage

admin.site.register(FAQ)
admin.site.register(FAQCategory)
admin.site.register(SupportMessage)
