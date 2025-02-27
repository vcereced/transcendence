from celery import shared_task
from game_app.models import Game, GameState
from game_app.serializers import GameSerializer
import redis
from game import settings as s
import json
from celery import Celery
from django.db import transaction
import random

# @shared_task(name='receive_order_processed_event')
# def receive_order_processed_event(processed_order_data):
#     order_id = processed_order_data.get('id')
#     if not order_id:
#         # Log the error and raise an exception
#         raise ValueError("Order ID is required to update an order.")

#     try:
#         order = Order.objects.get(pk=order_id)
#     except Order.DoesNotExist:
#         # Log the error and raise an exception
#         raise ValueError(f"Order with ID {order_id} does not exist.")

#     serializer = OrderSerializer(order, data=processed_order_data)
#     if not serializer.is_valid():
#         # Log the error and raise an exception
#         raise ValueError(f"Invalid order data: {serializer.errors}")

#     serializer.save()


# @shared_task(name="create_game")
# def create_game(game_data):
#     with transaction.atomic():
#         serializer = GameSerializer(data=game_data)
#         if not serializer.is_valid():
#             print(f"Game creation failed. Invalid game data: {serializer.errors}")
#             return
#         game = serializer.save()
#         redis_client = redis.Redis(host="redis", port=6379)
#         redis_client.set(f"game:{game.id}:ball", json.dumps(s.INITIAL_GAME_STATE["ball"]))
#         redis_client.set(f"game:{game.id}:left_paddle_y", json.dumps(s.INITIAL_GAME_STATE["left_paddle_y"]))
#         redis_client.set(f"game:{game.id}:right_paddle_y", json.dumps(s.INITIAL_GAME_STATE["right_paddle_y"]))
#         redis_client.set(f"game:{game.id}:scores", json.dumps(s.INITIAL_GAME_STATE["scores"]))
#         redis_client.rpush("game_queue", f"{game.id}")
############################################################################################################
#MODIFIED BY GARYDD1 FOR TESTING PURPOSES

redis_client = redis.Redis(host="redis", port=6379)

# @shared_task(name="create_game")
# def create_game(game_data):
#     """
#     Bypass: En lugar de crear un juego en la base de datos, enviamos directamente el evento game_end.
#     """

#     print(f"🚀 Bypass activado: Creando juego simulado con datos {game_data}")

#     # Simular un ganador aleatorio entre los dos jugadores
#     winner_id = game_data["left_player_id"] if random.choice([True, False]) else game_data["right_player_id"]
#     loser_id = game_data["right_player_id"] if winner_id == game_data["left_player_id"] else game_data["left_player_id"]
#     winner_username = game_data["left_player_username"] if winner_id == game_data["left_player_id"] else game_data["right_player_username"]
#     loser_username = game_data["right_player_username"] if winner_id == game_data["left_player_id"] else game_data["left_player_username"]
#     # Construir el mensaje para `game_end`
#     message = {
#         "winner": winner_username,
#         "loser": loser_username,
#         "tournament_id": game_data["tournament_id"],
#         "tree_id": game_data["tree_id"],
#         "type": "game_end",
#     }

#     print(f"🏆 Juego simulado finalizado. Ganador: {winner_username}, Perdedor: {loser_username}")

#     # Publicar el mensaje en Redis en el canal del torneo
#     channel = f"tournament_{game_data['tournament_id']}"
#     redis_client.publish(channel, json.dumps({"type": "game_end", **message}))

#     # Llamar directamente a `game_end`
#     # game_end(message)

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
    delay = random.randint(1, 4)
    print(f"Esperando {delay} segundos antes de enviar la tarea `game_end`")
    time.sleep(delay)
    print(f"Enviando tarea `game_end`")
    app.send_task(
        "game_end",
        args=[{
            "tournament_id": game_data["tournament_id"],
            "winner": winner_username,
            "loser": loser_username,
            "tree_id": game_data["tree_id"],
            "type": "game_end",
        }],
        queue="matchmaking_tasks",
    )

# async def send_game_end_task(self, winner):
#     #print en ROJO
#     print("\033[91m" + "send_game_end_task from GAME_APP")
    
#     loser = (
#         self.game.left_player_username
#         if winner == self.game.right_player_username
#         else self.game.right_player_username
#     )
#     print (f"winner: {winner}")
#     print (f"loser: {loser}")
#     message = {
#         "tournament_id": self.game.tournament_id,
#         "winner": winner,
#         "loser": loser,
#         "tree_id": self.game.tree_id,
#         "type": "game_end",

#     }

#     await app.send_task(
#         "game_end",
#         args=[message],
#         queue="matchmaking_tasks",
#     )


