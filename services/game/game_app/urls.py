from django.contrib import admin
from django.urls import path
from game_app import views

urlpatterns = [
    path('', views.GameList.as_view()),
    path('<int:pk>/', views.GameDetail.as_view()),
]