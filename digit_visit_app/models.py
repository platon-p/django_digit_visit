import datetime as dt

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.utils import timezone

User = get_user_model()


class SubscriptionType(models.Model):
    name = models.CharField('Название', max_length=30)
    price = models.IntegerField('Стоимость')
    duration = models.IntegerField('Продолжительность (в днях)')

    class Meta:
        verbose_name = 'Тип подписки'
        verbose_name_plural = 'Типы подписок'
        ordering = ['price']

    def __str__(self):
        return self.name


class DataType(models.Model):
    class Meta:
        verbose_name = 'Поле визитки'
        verbose_name_plural = 'Поля визитки'

    name = models.CharField('Название поля', max_length=100, unique=True)
    is_free = models.BooleanField('Бесплатный', default=False)
    required = models.BooleanField('Обязательный', default=False)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    user = models.ForeignKey('auth.User', models.CASCADE, verbose_name='Пользователь')
    subscription = models.ForeignKey('SubscriptionType', models.CASCADE, verbose_name='Тип подписки')
    start_date = models.DateTimeField(editable=False)
    end_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.start_date = dt.datetime.now()
        self.end_date = dt.datetime.now() + dt.timedelta(days=self.subscription.duration)
        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.subscription.name} подписка для {self.user.first_name} с {self.start_date} по {self.end_date}'


class Data(models.Model):
    user = models.ForeignKey('auth.User', models.CASCADE)
    data_type = models.ForeignKey('DataType', models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'{self.user.first_name if self.user.first_name else "Unknown"}`s {self.data_type.name}: {self.content}'

    def to_lst(self):
        return [self.user, self.data_type.name, self.content]


class Cards(models.Model):
    class Meta:
        verbose_name = 'Визитка'
        verbose_name_plural = 'Визитки'

    user = models.ForeignKey('auth.User', models.CASCADE)
    title = models.CharField(max_length=100)
    create_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.create_date = timezone.now()
        super(Cards, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}`s card ({self.title})'


class CardsContent(models.Model):
    card = models.ForeignKey('Cards', models.CASCADE)
    data = models.ForeignKey('Data', models.CASCADE)


from .utils import *


def user_signed_up_receiver(request: WSGIRequest, user: User, **kwargs):
    if user.first_name:
        add_user_data(user, 'Имя', user.first_name)
    if user.last_name:
        add_user_data(user, 'Фамилия', user.last_name)
    if user.email:
        add_user_data(user, 'Email', user.email)


user_signed_up.connect(user_signed_up_receiver, sender=User)
