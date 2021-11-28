from django.urls import path

from . import views

urlpatterns = [
    path('', views.http_response, name='home')
]
