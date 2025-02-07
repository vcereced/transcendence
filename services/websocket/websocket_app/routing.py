from django.urls import re_path
from websocket_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_name>\w+)/$', consumers.RoomConsumer.as_asgi()),
	re_path(r'ws/global_tournament_counter/$', consumers.TournamentCounterConsumer.as_asgi()),
]
