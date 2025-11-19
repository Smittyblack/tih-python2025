# internethub/tv/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tv_home, name='tv_home'),
]