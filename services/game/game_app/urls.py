from django.contrib import admin
from django.urls import path
from game_app import views

urlpatterns = [
    path("", views.GameList.as_view()),
    path("<int:pk>/", views.GameDetail.as_view()),
    path("trigger_create_game/", views.trigger_create_game_task),
    path("trigger_launch_game/", views.trigger_launch_game_task),
    path("active/", views.has_active_game),
    path("create/", views.create_game),
]
