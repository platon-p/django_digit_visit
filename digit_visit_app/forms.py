from django import forms

from .models import DataType

field_types = {
    'String': forms.CharField(),
    'Text': forms.CharField(widget=forms.Textarea),
    'Date': forms.DateField(),
    'Image': forms.ImageField(allow_empty_file=False),
    'Phone': forms.CharField(),
    'Email': forms.EmailField(),
}
field_types['Image'].widget.attrs['id'] = 'ImageField'


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if kwargs['is_free']:
            fields = DataType.objects.filter(is_free=True).all()
        else:
            fields = DataType.objects.filter().all()
        del kwargs['is_free']

        super().__init__(*args, **kwargs)

        self.fields['Название'] = forms.CharField(required=True)
        self.fields['Адрес визитки'] = forms.SlugField(required=True)
        self.fields['Адрес визитки'].widget.attrs['id'] = 'address'

        for i in fields:
            self.fields[i.name] = field_types[i.field_type]
            self.fields[i.name].required = i.required
