from django.contrib import admin

from .models import SubscriptionType, DataType, Subscription, Data

admin.site.register(SubscriptionType)
admin.site.register(DataType)
admin.site.register(Data)
admin.site.register(Subscription)
