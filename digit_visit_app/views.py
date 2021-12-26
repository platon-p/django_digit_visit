import datetime as dt

from allauth.account.views import LoginView, SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from digit_visit_app.models import Cards, Subscription, Data, DataType, CardsContent
from .forms import CreateForm


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
        context['subscription'] = ''
        context['subscription_is_active'] = False
        if subs:
            sub = subs[len(subs) - 1]
            if sub.end_date.date() >= dt.date.today():
                context['subscription'] = sub
                context['subscription_is_active'] = True
            context['time_left'] = (sub.end_date.date() - dt.date.today()).days
        user_info = list(Data.objects.filter(user=self.request.user).all())
        user_info = [i.to_lst() for i in user_info]
        context['user_info'] = {i[1]: i[2] for i in user_info}
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


def create_page_view(request: WSGIRequest):
    subs = Subscription.objects.filter(user=request.user).all()
    subscription_is_active = False
    if subs:
        sub = subs[len(subs) - 1]
        if sub.end_date.date() >= dt.date.today():
            subscription_is_active = True
    domain = Site.objects.get_current().domain + '/v/'
    form = CreateForm(request.POST, is_free=not subscription_is_active)

    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'create_page.html', {'form': form, 'domain': domain})
        if Cards.objects.filter(slug=form.data['Адрес визитки']):
            form.errors['Адрес визитки'] = 'Адрес уже занят'
            return render(request, 'create_page.html', {'form': form, 'domain': domain})
        a = {DataType.objects.filter(name=key).first(): val for key, val in form.data.items() if
             key != 'csrfmiddlewaretoken' or val}

        card = Cards(user=request.user, title=form.data['Название'], slug=form.data['Адрес визитки'])
        card.save()

        for key, val in a.items():
            if val is None or key is None:
                continue
            data = Data(user=request.user, data_type=key, content=val)
            exist = Data.objects.filter(user=request.user, data_type=key).last()
            if not exist:
                data.save()
                card_content = CardsContent(card=card, data=data)
            else:
                card_content = CardsContent(card=card, data=exist)
            card_content.save()
        return redirect(reverse('profile'))
    else:
        user_data = Data.objects.filter(user=request.user).all()
        user_data = {i.to_lst()[1]: i.to_lst()[2] for i in user_data}
        form = CreateForm(is_free=not subscription_is_active, initial=user_data)
        domain = Site.objects.get_current().domain + '/v/'
        return render(request, 'create_page.html', {'form': form, 'domain': domain})


class ShowCardView(TemplateView):
    template_name = 'show_card.html'

    def get_context_data(self, **kwargs):
        a = get_object_or_404(Cards, slug=self.kwargs['slug'])
        card_content = CardsContent.objects.filter(card=a).all()

        card_content = {i.data.data_type.name: i.data.content for i in card_content}
        context = {'card_content': card_content}
        return context
