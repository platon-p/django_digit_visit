from allauth.account.views import LoginView, SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView, FormView

from digit_visit_app.models import Cards, create_card, Subscription, DataType
import datetime as dt


class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarifs = [
            ['Free', ['Фамилия, имя', 'Фото', 'Возраст', 'Должность', 'Номер телефона', 'Эл. почта', 'Поле "о себе"'],
             'Бесплатно', ''],
            ['Pro',
             ['Все возможности Free', 'До трёх ссылок', 'Мессенджеры', 'Соцсети', 'Экспорт в контакты', 'Портфолио',
              'Образование'], '799 руб/год', 'или 99 руб/мес'],
            ['Business',
             ['Все возможности Pro', 'Название компании', 'Адрес офиса', 'Выгоднее при использовании для бизнеса'],
             '5 990 руб/год', 'за 10 сотрудников']
        ]
        questions = [
            ['Как поделиться визиткой?',
             'Создав визитку, нажмите "поделиться", после чего скопируйте ссылку или QR-код и отправьте собеседнику'],
            ['Как работает экспорт в контакты?',
             'На основе данных вашего профиля система создает контакт, который можно скачать и добавить в записную книжку'],
            ['Я могу добавить соцсеть, которой нет в списке?',
             'Помимо Vk, Facebook, Instagram вы можете добавить до трех собственных ссылок, например, на ваш личный сайт, '
             'или сайт компании']
        ]
        context['tarifs'] = tarifs
        context['questions'] = questions
        return context


class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cards'] = Cards.objects.filter(user=self.request.user)

        subs = Subscription.objects.filter(user=self.request.user).all()
        subs = subs[len(subs) - 1]
        context['time_left'] = subs.end_date.date() - dt.date.today()
        if subs.subscription.price > 0 and subs.end_date.date() >= dt.datetime.now().date():
            context['subscription'] = subs
            context['is_free'] = False
        else:
            context['is_free'] = True
            context['subscription'] = ''
        return context


class LoginPageView(LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context


class RegisterPageView(SignupView):
    template_name = 'register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form']['email'].field.required = True
        context['title'] = 'Регистрация'
        return context


class CreatePageView(TemplateView):
    template_name = 'create_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subs = Subscription.objects.filter(user=self.request.user).all()
        subs = subs[len(subs) - 1]
        context['is_free'] = not (subs.subscription.price > 0 and subs.end_date.date() >= dt.datetime.now().date())
        context['fields'] = DataType.objects.filter(is_free=context['is_free']).all()
        return context

    def setup(self, request, *args, **kwargs):
        print(11)
        super().setup(request, *args, **kwargs)


def create_page_view(request):
    try:
        create_card(request.user, 'Hello')
        return HttpResponse('Success')
    except Exception as e:
        return HttpResponse(f':(((\n{e}')
