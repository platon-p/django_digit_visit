from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('profile', views.ProfilePageView.as_view(), name='profile_page'),
    path('accounts/login/', views.LoginPageView.as_view(), name='login_page'),
    path('accounts/signup/', views.RegisterPageView.as_view(), name='signup_page'),
    path('create', views.create_page_view, name='create'),
]
