from django.contrib.auth.models import User

from .models import DataType, Data, Cards, Subscription
import datetime as dt


def add_user_data(user: User, data_name: str, content: str):
    data = Data()
    data.user = user
    data.data_type = DataType.objects.filter(name=data_name)[0]
    data.content = content
    data.save()


def calculate_age(birthdate) -> str:
    birthdate = dt.datetime.strptime(birthdate, '%d.%m.%Y').date()
    age = str(dt.date.today().year - birthdate.year - (
            (dt.date.today().month, dt.date.today().day) < (birthdate.month, birthdate.day)
    ))
    if age[-1] == '1':
        return age + ' год'
    elif age[-1] in '234':
        return age + ' года'
    elif age[-1] in '567890':
        return age + ' лет'


def is_subscribe_active(user: User) -> bool:
    subs = Subscription.objects.filter(user=user).all()
    if subs:
        sub = subs[len(subs) - 1]
        if sub.end_date.date() >= dt.date.today():
            return True
    return False
