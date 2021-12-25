import datetime as dt

from allauth.account.views import LoginView, SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView
from django.contrib.sites.models import Site

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


class CreatePageView(FormView):
    template_name = 'create_page.html'
    form_class = CreateForm
    success_url = '/profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subs = Subscription.objects.filter(user=self.request.user).all()
        context['subscription_is_active'] = False

        if subs:
            sub = subs[len(subs) - 1]
            if sub.end_date.date() >= dt.date.today():
                context['subscription_is_active'] = True
        return context

    def form_valid(self, form):
        return redirect(self.success_url)


def create_page_view(request: WSGIRequest):
    subs = Subscription.objects.filter(user=request.user).all()
    subscription_is_active = False
    if subs:
        sub = subs[len(subs) - 1]
        if sub.end_date.date() >= dt.date.today():
            subscription_is_active = True

    if request.method == 'POST':
        form = CreateForm(request.POST, is_free=not subscription_is_active)
        if not form.is_valid():
            return render(request, 'create_page.html', {'form': form})
        a = {DataType.objects.filter(name=i[0]).first(): i[1] for i in form.data.items() if
             i[0] != 'csrfmiddlewaretoken' or i[1]}
        card = Cards(user=request.user, title=form.data['Название'])
        card.save()
        for i in a.items():
            if i[0] is None:
                continue
            data = Data(user=request.user, data_type=i[0], content=i[1])
            data.save()
            card_content = CardsContent(card=card, data=data)
            card_content.save()

        return redirect('/profile')
    user_data = Data.objects.filter(user=request.user).all()
    user_data = {i.to_lst()[1]: i.to_lst()[2] for i in user_data}
    form = CreateForm(is_free=not subscription_is_active, initial=user_data)
    domain = Site.objects.get_current().domain + '/v/'
    return render(request, 'create_page.html', {'form': form, 'domain': domain})
