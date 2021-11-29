from django.contrib.auth.models import User

from .models import DataType, Data


def add_user_data(user: User, data_name: str, content: str):
    data = Data()
    data.user = user
    data.data_type = DataType.objects.filter(name=data_name)[0]
    data.content = content
    data.save()