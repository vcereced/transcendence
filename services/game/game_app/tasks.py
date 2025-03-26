from celery import shared_task
from game_app.models import Game, GameState, RockPaperScissorsGame
from game_app.serializers import GameSerializer, RockPaperScissorsGameSerializer
import redis
from game import settings as s
import json
from celery import Celery
from django.db import transaction
import random


# @shared_task(name="create_game")
# def create_game(game_data):
#     with transaction.atomic():
#         serializer = RockPaperScissorsGameSerializer(data=game_data)
#         if not serializer.is_valid():
#             print(
#                 f"Rock paper scissors game creation failed. Invalid game data: {serializer.errors}"
#             )
#             return
#         rps_record = serializer.save()
#         redis_client = redis.Redis(host="redis", port=6379)
#         redis_client.set(f"rps:{rps_record.id}:time_left", str(s.RPS_GAME_TIMER_LENGTH))
#         redis_client.set(
#             f"rps:{rps_record.id}:left_choice", str(random.choice(s.RPS_CHOICES))
#         )
#         redis_client.set(
#             f"rps:{rps_record.id}:right_choice", str(random.choice(s.RPS_CHOICES))
#         )
#         redis_client.set(f"rps:{rps_record.id}:winner_username", "")
#         redis_client.set(f"rps:{rps_record.id}:is_finished", "0")
#         redis_client.rpush("rps_queue", f"{rps_record.id}")


# @shared_task(name="launch_game")
# def launch_game(game_data):
#     with transaction.atomic():
#         serializer = GameSerializer(data=game_data)
#         if not serializer.is_valid():
#             print(f"Game creation failed. Invalid game data: {serializer.errors}")
#             return
#         game = serializer.save()
#         redis_client = redis.Redis(host="redis", port=6379)
#         redis_client.set(
#             f"game:{game.id}:ball", json.dumps(s.INITIAL_GAME_STATE["ball"])
#         )
#         redis_client.set(
#             f"game:{game.id}:left_paddle_y",
#             json.dumps(s.INITIAL_GAME_STATE["left_paddle_y"]),
#         )
#         redis_client.set(
#             f"game:{game.id}:right_paddle_y",
#             json.dumps(s.INITIAL_GAME_STATE["right_paddle_y"]),
#         )
#         redis_client.set(
#             f"game:{game.id}:scores", json.dumps(s.INITIAL_GAME_STATE["scores"])
#         )
#         redis_client.set(f"game:{game.id}:winner_username", "")
#         redis_client.set(f"game:{game.id}:is_finished", "0")
#         redis_client.set(f"game:{game.id}:start_countdown", str(s.START_COUNTDOWN))
#         redis_client.set(f"game:{game.id}:next_side_to_collide", "left")
#         redis_client.rpush("game_queue", f"{game.id}")


# ############################################################################################################
#MODIFIED BY GARYDD1 FOR TESTING PURPOSES

redis_client = redis.Redis(host="redis", port=6379)



app = Celery('game', broker='amqp://guest:guest@message-broker:5672//')
import time

@shared_task(name="create_game")
def create_game(game_data):
    """
    Bypass: En lugar de crear un juego en la base de datos, enviamos directamente el evento game_end.
    """

    print(f"🚀 Bypass activado: Creando juego simulado con datos {game_data}")

    # Simular un ganador aleatorio entre los dos jugadores
    winner_id = game_data["left_player_id"] if random.choice([True, False]) else game_data["right_player_id"]
    loser_id = game_data["right_player_id"] if winner_id == game_data["left_player_id"] else game_data["left_player_id"]
    winner_username = game_data["left_player_username"] if winner_id == game_data["left_player_id"] else game_data["right_player_username"]
    loser_username = game_data["right_player_username"] if winner_id == game_data["left_player_id"] else game_data["left_player_username"]

    print(f"🏆 Juego simulado finalizado. Ganador: {winner_username}, Perdedor: {loser_username}")

    # Enviar la tarea `game_end` a Celery
    #hacer un delay temporal antes de enviar la tarea
    delay = random.randint(1, 6)
    print(f"Esperando {delay} segundos antes de enviar la tarea `game_end`")
    time.sleep(delay)
    print(f"Enviando tarea `game_end`")
    app.send_task(
        "game_end",
        args=[{
            "tournament_id": game_data["tournament_id"],
            "winner": winner_username,
            "loser": loser_username,
            "tree_index": game_data["tree_index"],
            "type": "game_end",
        }],
        queue="matchmaking_tasks",
    )