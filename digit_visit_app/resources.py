from import_export import resources

from .models import DataType


class DataTypeResource(resources.ModelResource):
    class Meta:
        model = DataType
