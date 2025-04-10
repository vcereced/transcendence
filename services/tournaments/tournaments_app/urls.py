from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_tournament, name='create_tournament'),
    path('list', views.list_tournaments, name='list_tournaments'),
    path('<int:tournament_id>/join', views.join_tournament, name='join_tournament'),
	path('player_counts', views.list_tournament_player_counts, name='list_tournament_player_counts'),
    path('<int:tournament_id>/name', views.get_tournament_name, name='get_tournament_name'),
    path('user/<int:user_id>/tournament-stats', views.UserTournamentStatsAPIView.as_view(), name='user_tournament_stats'),
    
]
