from game_app.models import Game
from game_app.serializers import GameSerializer
from rest_framework import generics
from celery import current_app
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from game_app import tasks


class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


@api_view(["POST"])
def trigger_create_game_task(request):
    current_app.send_task(
        "create_game",
        args=[request.data],
        queue="game_tasks",
    )
    return Response(status=status.HTTP_200_OK)
