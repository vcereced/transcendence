from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register_tournament_api, name='register_tournament'),
    path('get_tournament/<int:tournament_id>', views.get_tournament_details, name='get_tournament'),
    path('get_tournaments_ids', views.get_tournaments_ids, name='get_tournaments_ids'),
]