import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis
import asyncio
import jwt
import random


class TournamentCounterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Establecer la conexión con el WebSocket
        print("Connecting to global WebSocket")

        # Conectar a Redis
        self.redis = redis.from_url("redis://redis:6379")  # Conexión a Redis
        # Canal de Django para el WebSocket global
        self.room_group_name = (
            "global_tournament_counter"  # Canal global para todos los torneos
        )

        # Crear un objeto pubsub para escuchar el canal de Redis
        self.pubsub = self.redis.pubsub()

        # Suscribirse al canal de Redis 'tournaments_channel'
        await self.pubsub.subscribe("tournaments_channel")

        # Añadir el canal del WebSocket al grupo global de canales de Django
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Aceptar la conexión WebSocket
        await self.accept()

        # Iniciar el bucle para escuchar los mensajes de Redis
        asyncio.create_task(self.listen_to_redis())

    async def listen_to_redis(self):
        # Bucle para escuchar los mensajes en el canal de Redis
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                # Procesamos el mensaje recibido
                print(f"Received message from Redis: {message}")
                if message["type"] == "message":
                    # Extraemos los datos del mensaje
                    data = json.loads(message["data"])
                    tournament_id = data.get("tournamentId")
                    user_count = data.get("user_count")

                    if tournament_id and user_count is not None:
                        # Enviar los datos de actualización a todos los clientes conectados
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "tournamentId": tournament_id,
                                    "user_count": user_count,
                                }
                            )
                        )

    async def disconnect(self, close_code):
        # Quitar el canal del grupo global
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Manejar cualquier mensaje recibido (por ejemplo, actualizaciones de contador de jugadores)
        pass

    async def update_user_count(self, tournament_id, user_count):
        # Actualizar el contador de jugadores en todos los torneos a través del WebSocket global
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "tournament_user_count",
                "tournament_id": tournament_id,
                "user_count": user_count,
            },
        )

    async def tournament_user_count(self, event):
        # Recibir actualizaciones del contador de jugadores de Redis
        tournament_id = event["tournament_id"]
        user_count = event["user_count"]

        # Enviar la actualización a todos los clientes conectados
        await self.send(
            text_data=json.dumps(
                {"tournamentId": tournament_id, "user_count": user_count}
            )
        )


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting to specific tournament WebSocket")
        self.user = self.scope.get("user")

        # Obtener el nombre del torneo desde la URL
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = (
            f"tournament_{self.room_name}"  # Canal específico del torneo
        )

        # Conectar a Redis
        self.redis = redis.from_url("redis://redis:6379")

        # Definir la clave para el contador de jugadores en este torneo
        self.user_count_key = f"{self.room_group_name}_player_count"

        # Añadir el canal al grupo del torneo
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Incrementar el contador de jugadores en Redis
        print("Incrementing player count", self.user_count_key)

        current_user_count = await self.redis.incr(self.user_count_key)

        # Publicar actualización en Redis (para el consumidor global)
        await self.publish_global_update(current_user_count)

        # FOR TESTING PURPOSES. HERE WE CAN OBTAIN THE JWT TOKEN FROM THE SCOPE

        headers = dict(self.scope["headers"])
        cookie_header = headers[b"cookie"]
        if cookie_header:
            for c in cookie_header.decode().split(";"):
                if "accessToken" in c:
                    print("access token found:")
                    jwt_token = c.split("=")[1]
                    print(jwt_token)
                    try:
                        payload = jwt.decode(
                            jwt_token, options={"verify_signature": False}
                        )
                        print("Decoded Payload:", payload)

                        username = payload.get("username")
                        self.username = username
                        print(f"Username: {username}")
                    except jwt.DecodeError as e:
                        print(f"Error decoding token: {e}")
                    break
        print("publishing local update")
        await self.redis.set(f"user_channel:{self.username}", self.channel_name)
        await self.redis.sadd(
            f"{self.room_group_name}_users", username
        )  # Create a set of users in the tournament
        await self.publish_local_update()
        print("sending message directly to user")
        await self.send_message("Hello from the server mr. " + self.username)
        # Aceptar la conexión WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Quitar el canal del grupo del torneo
        print(f"User {self.username} disconnected")
        await self.redis.srem(f"{self.room_group_name}_users", self.username)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.publish_local_update()

        # Disminuir el contador de jugadores en Redis
        current_user_count = await self.redis.decr(self.user_count_key)

        # Publicar actualización en Redis (para el consumidor global)
        await self.publish_global_update(current_user_count)

    async def publish_global_update(self, user_count):
        """Publica la actualización de conteo en el canal de Redis global."""
        message = {
            "tournamentId": self.room_name,  # El ID del torneo (extraído de la URL)
            "user_count": user_count,
        }
        await self.redis.publish("tournaments_channel", json.dumps(message))

    async def publish_local_update(self):
        "Publica actualizacion de nombres de usuarios en el canal de Redis local"
        user_list = await self.redis.smembers(f"{self.room_group_name}_users")
        decoded_user_list = [user.decode("utf-8") for user in user_list]
        message = {"tournamentId": self.room_name, "user_list": decoded_user_list}
        await self.redis.publish(self.room_group_name, json.dumps(message))
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_list", "user_list": decoded_user_list}
        )

    async def user_list(self, event):
        """Maneja el mensaje de tipo 'user_list'."""

        # Sends the updated user list to the client
        await self.send(
            text_data=json.dumps({"type": "user_list", "user_list": event["user_list"]})
        )

    async def update_user_count(self):
        # Obtener el número actualizado de jugadores en este torneo
        current_user_count = await self.redis.get(self.user_count_key)

        # Enviar el número actualizado de jugadores conectados a todos los usuarios del torneo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_count",
                "count": (
                    int(current_user_count) if current_user_count is not None else 0
                ),
            },
        )

    async def user_count(self, event):
        # Recibe el número actualizado de jugadores conectados en el torneo y lo envía al WebSocket
        count = event["count"]
        await self.send(text_data=json.dumps({"user_count": count}))

    async def send_message(self, message):
        # Send message to specific channel
        channel_name = await self.redis.get(f"user_channel:{self.username}")

        if channel_name:
            await self.channel_layer.send(
                channel_name.decode("utf-8"),
                {"type": "direct_message", "message": message},
            )

    async def direct_message(self, event):
        # Receive message from room group
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

