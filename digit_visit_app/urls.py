from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('profile', views.ProfilePageView.as_view(), name='profile_page'),
]
