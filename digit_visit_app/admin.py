from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin, ImportExportMixin

from .models import *
from .resources import DataTypeResource


class DataTypeAdmin(ImportExportActionModelAdmin, ImportExportMixin):
    resource_class = DataTypeResource


admin.site.register(SubscriptionType)
admin.site.register(Data)
admin.site.register(Subscription)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(Cards)
admin.site.register(CardsContent)
