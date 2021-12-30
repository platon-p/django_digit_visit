import datetime as dt

from allauth.account.decorators import login_required
from allauth.account.signals import user_signed_up
from allauth.account.views import LoginView, SignupView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from digit_visit_app.models import Cards, Subscription, Data, CardsContent
from .forms import CreateForm
from .utils import calculate_age, add_user_data, is_subscribe_active

User = get_user_model()
domain = Site.objects.get_current().domain


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
        context['domain'] = domain
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


def user_signed_up_receiver(request: WSGIRequest, user: User, **kwargs):
    if user.first_name:
        add_user_data(user, 'Имя', user.first_name)
    if user.last_name:
        add_user_data(user, 'Фамилия', user.last_name)
    if user.email:
        add_user_data(user, 'Email', user.email)


user_signed_up.connect(user_signed_up_receiver, sender=User)


@login_required
def create_page_view(request: WSGIRequest):
    subscription_is_active = is_subscribe_active(request.user)
    if request.method == 'POST':
        form = CreateForm(request.POST or None, request.FILES or None, is_free=not subscription_is_active)
        if form.is_valid():
            form.save(request)
            return redirect(reverse('profile_page'))
    else:
        user_data = Data.objects.filter(user=request.user).all()
        user_data = {i.to_lst()[1]: i.to_lst()[2] for i in user_data}
        form = CreateForm(is_free=not subscription_is_active, initial=user_data)
    return render(request, 'create_page.html', {'form': form, 'domain': domain + '/v/'})


@login_required
def edit_page_view(request: WSGIRequest):
    pass


class ShowCardView(TemplateView):
    template_name = 'show_card.html'

    def get_context_data(self, **kwargs):
        card = get_object_or_404(Cards, slug=self.kwargs['slug'])
        card_content = CardsContent.objects.filter(card=card).all()
        active = is_subscribe_active(self.request.user)
        card_content = {i.data.data_type.name: i.data.content for i in card_content
                        if i.data.data_type.is_free in (True, not active)}
        card_content['Изображение'] = card.image.url
        # считаем возраст
        age = calculate_age(card_content.get('Дата рождения'))
        if age:
            card_content['Возраст'] = age

        context = {'card_content': card_content, 'domain': domain}

        return context
