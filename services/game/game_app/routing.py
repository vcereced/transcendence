from django.urls import re_path
from game_app import consumers

websocket_urlpatterns = [
    re_path(r"ws/game/pong/$", consumers.PlayerConsumer.as_asgi()),
    re_path(r"ws/game/rock-paper-scissors/$", consumers.RockPaperScissorsConsumer.as_asgi()),
]
