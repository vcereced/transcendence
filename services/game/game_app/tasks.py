from celery import shared_task
from game_app.models import Game, GameState, RockPaperScissorsGame
from game_app.serializers import GameSerializer, RockPaperScissorsGameSerializer
import redis
from game import settings as s
import json
from celery import current_app
from django.db import transaction
import random


@shared_task(name="create_game")
def create_game(game_data):
    with transaction.atomic():
        serializer = RockPaperScissorsGameSerializer(data=game_data)
        if not serializer.is_valid():
            print(
                f"Rock paper scissors game creation failed. Invalid game data: {serializer.errors}"
            )
            return
        rps_record = serializer.save()
        redis_client = redis.Redis(host="redis", port=6379)
        redis_client.set(f"rps:{rps_record.id}:time_left", str(s.RPS_GAME_TIMER_LENGTH))
        redis_client.set(
            f"rps:{rps_record.id}:left_choice", str(random.choice(s.RPS_CHOICES))
        )
        redis_client.set(
            f"rps:{rps_record.id}:right_choice", str(random.choice(s.RPS_CHOICES))
        )
        redis_client.set(f"rps:{rps_record.id}:winner_username", "")
        redis_client.set(f"rps:{rps_record.id}:is_finished", "0")
        redis_client.rpush("rps_queue", f"{rps_record.id}")


@shared_task(name="launch_game")
def launch_game(game_data):
    with transaction.atomic():
        serializer = GameSerializer(data=game_data)
        if not serializer.is_valid():
            print(f"Game creation failed. Invalid game data: {serializer.errors}")
            return
        game = serializer.save()
        redis_client = redis.Redis(host="redis", port=6379)
        redis_client.set(
            f"game:{game.id}:ball", json.dumps(s.INITIAL_GAME_STATE["ball"])
        )
        redis_client.set(
            f"game:{game.id}:left_paddle_y",
            json.dumps(s.INITIAL_GAME_STATE["left_paddle_y"]),
        )
        redis_client.set(
            f"game:{game.id}:right_paddle_y",
            json.dumps(s.INITIAL_GAME_STATE["right_paddle_y"]),
        )
        redis_client.set(
            f"game:{game.id}:scores", json.dumps(s.INITIAL_GAME_STATE["scores"])
        )
        redis_client.set(f"game:{game.id}:winner_username", "")
        redis_client.set(f"game:{game.id}:is_finished", "0")
        redis_client.rpush("game_queue", f"{game.id}")
