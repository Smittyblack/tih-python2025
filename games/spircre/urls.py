from django.urls import path
from . import views

app_name = 'spircre'

urlpatterns = [
    path('', views.spircre_game, name='game'),
    path('high_scores/', views.get_high_scores, name='high_scores'),
    path('inventory/', views.get_inventory, name='inventory'),
]