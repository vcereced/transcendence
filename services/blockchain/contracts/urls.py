from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register_tournament_api, name='register_tournament'),
    # path('get_tournament', views.get_tournament_api, name='get_tournament'),
    # path('get_winner', views.get_winner_api, name='get_winner'),
    # path('get_tree_hash', views.get_tree_hash_api, name='get_tree_hash'),
]