from django import forms

from .models import DataType


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if kwargs['is_free']:
            fields = DataType.objects.filter(is_free=kwargs['is_free']).all()
        else:
            fields = DataType.objects.filter().all()
        del kwargs['is_free']
        super().__init__(*args, **kwargs)
        self.fields['Название'] = forms.CharField(required=True)
        self.fields['Адрес визитки'] = forms.SlugField(required=True)
        self.fields['Адрес визитки'].widget.attrs['id'] = 'address'

        for i in fields:
            self.fields[i.name] = forms.CharField(required=i.required)
