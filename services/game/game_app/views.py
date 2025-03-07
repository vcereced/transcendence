import jwt
from django.db.models import Q

from game_app.models import Game, RockPaperScissorsGame
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

@api_view(["POST"])
def trigger_launch_game_task(request):
    current_app.send_task(
        "launch_game",
        args=[request.data],
        queue="game_tasks",
    )
    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
def has_active_game(request):
    headers = dict(request.headers)
    user_data = {}
    cookie_header = headers.get("cookie")
    if cookie_header:
        for c in cookie_header.decode().split(";"):
            if "accessToken" in c:
                jwt_token = c.split("=")[1]
                try:
                    payload = jwt.decode(
                        jwt_token, options={"verify_signature": False}
                    )
                    user_data["username"] = payload.get("username")
                    user_data["user_id"] = payload.get("user_id")
                except jwt.DecodeError as e:
                    print(f"Error decoding token: {e}")
                break
    
    if user_data.get("user_id"):
        response = {"has_active_pong_game": False, "has_active_rps_game": False}
        try:
            game = Game.objects.get(
            (
                Q(left_player_id=user_data["user_id"])
                | Q(right_player_id=user_data["user_id"])
            )
            & Q(is_finished=False)
        )
        except Game.MultipleObjectsReturned:
            return Response(
                {"error": "Multiple active games found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Game.DoesNotExist:
            game = None

        try:
            rps_game = RockPaperScissorsGame.objects.get(
                Q(player_1_id=user_data["user_id"]) | Q(player_2_id=user_data["user_id"])
                & Q(is_finished=False)
            )
        except RockPaperScissorsGame.MultipleObjectsReturned:
            return Response(
                {"error": "Multiple active rps games found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except RockPaperScissorsGame.DoesNotExist:
            rps_game = None

        if rps_game:
            response["has_active_rps_game"] = True
        elif game:
            response["has_active_pong_game"] = True
        
        return Response(response, status=status.HTTP_200_OK)






