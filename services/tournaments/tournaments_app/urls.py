from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_tournament, name='create_tournament'),
    path('', views.list_tournaments, name='list_tournaments'),
    path('<int:tournament_id>/join', views.join_tournament, name='join_tournament'),
]
