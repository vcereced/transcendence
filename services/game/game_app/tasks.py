from celery import shared_task
from game_app.models import Game, GameState
from game_app.serializers import GameSerializer
import redis
from game import settings as s
import json
from celery import current_app
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


@shared_task(name="create_game")
def create_game(game_data):
    with transaction.atomic():
        serializer = GameSerializer(data=game_data)
        if not serializer.is_valid():
            print(f"Game creation failed. Invalid game data: {serializer.errors}")
        game = serializer.save()
        redis_client = redis.Redis(host="redis", port=6379)
        redis_client.set(f"game:{game.id}:ball", json.dumps(s.INITIAL_GAME_STATE["ball"]))
        redis_client.set(f"game:{game.id}:left_paddle_y", json.dumps(s.INITIAL_GAME_STATE["left_paddle_y"]))
        redis_client.set(f"game:{game.id}:right_paddle_y", json.dumps(s.INITIAL_GAME_STATE["right_paddle_y"]))
        redis_client.set(f"game:{game.id}:scores", json.dumps(s.INITIAL_GAME_STATE["scores"]))
        redis_client.rpush("game_queue", f"{game.id}")
