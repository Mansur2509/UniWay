from django.contrib import admin

from .models import Subscription, UsageLimit, UsageLog

admin.site.register(Subscription)
admin.site.register(UsageLimit)
admin.site.register(UsageLog)

