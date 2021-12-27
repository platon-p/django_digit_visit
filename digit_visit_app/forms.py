from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import DataType, Cards, Data, CardsContent

field_types = {
    'String': forms.CharField(),
    'Text': forms.CharField(widget=forms.Textarea),
    'Date': forms.DateField(),
    'Phone': forms.CharField(),
    'Email': forms.EmailField(),
}


def validate_card(value):
    if Cards.objects.filter(slug=value):
        raise ValidationError(
            _('Этот адрес уже занят'),
        )


class CreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if kwargs['is_free']:
            fields = DataType.objects.filter(is_free=True).all()
        else:
            fields = DataType.objects.filter().all()
        del kwargs['is_free']

        super().__init__(*args, **kwargs)

        self.fields['Название'] = forms.CharField(required=False)
        self.fields['Адрес визитки'] = forms.SlugField(required=True, validators=[validate_card])
        self.fields['Адрес визитки'].widget.attrs['id'] = 'address'
        self.fields['Изображение'] = forms.ImageField(required=True)

        self.custom_fields = []
        for field in fields:
            self.fields[field.name] = field_types[field.field_type]
            self.fields[field.name].required = field.required
            self.custom_fields.append(field)

    def save(self, request: WSGIRequest):
        # Создаем визитку
        card = Cards(
            user=request.user,
            title=self.data.get('Название', 'Новая визитка 1'),
            slug=self.data.get('Адрес визитки'),
            image=self.files.get('Изображение')
        )
        card.save()

        for data_type in self.custom_fields:
            val = self.data.get(data_type.name, False)
            if not val:
                continue
            exist = Data.objects.filter(user=request.user, data_type=data_type, content=val).last()
            if not exist:
                data = Data(user=request.user, data_type=data_type, content=val)
                data.save()
                card_content = CardsContent(card=card, data=data)
            else:
                card_content = CardsContent(card=card, data=exist)
            card_content.save()
