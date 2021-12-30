from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import DataType, Cards, Data, CardsContent

field_types = {
    'String': forms.CharField,
    'Text': forms.CharField,
    'Date': forms.DateField,
    'Phone': forms.CharField,
    'Email': forms.EmailField,
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
            self.fields[field.name] = field_types[field.field_type](required=field.required)
            if field.field_type == 'Date':
                self.fields[field.name].widget.attrs['placeholder'] = 'дд.мм.гггг'
            elif field.field_type == 'Text':
                self.fields[field.name].widget = forms.Textarea()
            self.custom_fields.append(field)

    def save(self, request: WSGIRequest):
        # Создаем визитку
        card = Cards(
            user=request.user,
            title=self.data.get('Название') or 'Новая визитка',
            slug=self.data.get('Адрес визитки'),
            image=self.files.get('Изображение')
        )
        card.save()

        for data_type in self.custom_fields:
            val = self.data.get(data_type.name, False)
            if not val:
                continue
            data = Data(user=request.user, data_type=data_type, content=val)
            data.save()
            card_content = CardsContent(card=card, data=data)
            card_content.save()


class EditForm(forms.Form):
    def __init__(self, card: Cards, card_content: list[CardsContent], active: bool, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.card = card
        self.card_content = card_content
        self.active = active

        self.fields['Название'] = forms.CharField(required=False, initial=card.title)
        self.fields['Адрес визитки'] = forms.SlugField(required=True, initial=card.slug)
        self.fields['Адрес визитки'].widget.attrs['id'] = 'address'
        self.fields['Изображение'] = forms.ImageField(required=False)
        self.image_url = card.image.url

        for field in card_content:
            self.fields[field.data.data_type.name] = field_types[field.data.data_type.field_type](
                required=field.data.data_type.required,
                initial=field.data.content,
                disabled=not active and not field.data.data_type.is_free,
            )
            if self.fields[field.data.data_type.name].disabled:
                self.message = 'Некоторые поля недоступны, так как ваша подписка неактивна'
            if field.data.data_type.field_type == 'Text':
                self.fields[field.data.data_type.name].widget = forms.Textarea()
            if field.data.data_type.field_type == 'Date':
                self.fields[field.data.data_type.name].widget.attrs['placeholder'] = 'дд.мм.гггг'

    def save(self):
        for key, val in self.data.items():
            if key == 'csrfmiddlewaretoken':
                continue
            elif key == 'Название':
                self.card.title = val
            elif key == 'Адрес':
                self.card.slug = val
            elif key == 'Изображение':
                if val:
                    self.card.image = val
            else:
                for i in range(len(self.card_content)):
                    if self.card_content[i].data.data_type.name == key:
                        self.card_content[i].data.content = val
                        self.card_content[i].data.save(force_update=True)
        self.card.save()
