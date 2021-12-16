from django import forms
from .models import DataType


class CreateFreeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = DataType.objects.filter(is_free=True).all()
        for i in fields:
            self.fields[i.name] = forms.CharField(required=i.required)
