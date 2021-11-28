import datetime as dt

from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db import models


class SubscriptionType(models.Model):
    id = models.AutoField(primary_key=True, unique=True)

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

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField('Название поля', max_length=100, unique=True)
    is_free = models.BooleanField('Бесплатный', default=False)
    required = models.BooleanField('Обязательный', default=False)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, models.CASCADE)
    subscription = models.ForeignKey(SubscriptionType, models.CASCADE)
    start_date = models.DateTimeField(editable=False)
    end_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        self.start_date = dt.datetime.now()
        self.end_date = dt.datetime.now() + dt.timedelta(days=self.subscription.duration)


class Data(models.Model):
    id = models.AutoField(primary_key=True, unique=False)
    user = models.ForeignKey(User, models.CASCADE)
    data_type = models.ForeignKey(DataType, models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f'{self.user.first_name}`s {self.data_type.name}: {self.content}'


from .utils import *


def user_signed_up_receiver(request: WSGIRequest, user: User, **kwargs):
    if user.first_name:
        add_user_data(user, 'Имя', user.first_name)
    if user.last_name:
        add_user_data(user, 'Фамилия', user.last_name)
    if user.email:
        add_user_data(user, 'Email', user.email)


user_signed_up.connect(user_signed_up_receiver, sender=User)
