import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis
import asyncio
import jwt
from websocket_app import serializers, models
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


class GameConsumer(AsyncWebsocketConsumer):

    group_tasks = {}
    field_width = 600
    field_height = 400
    ball_radius = field_width / 50
    paddle_height = field_height / 4
    paddle_width = field_width / 50
    paddle_move_amount = 5
    ball_speed_increment = 1.3
    is_colliding = False

    async def connect(self):

        await self.accept()

        if not await self.initialize_user():
            return

        if not await self.initialize_game_state():
            return

        await self.add_connection_to_group()

        if self.game_group_name not in self.group_tasks:
            self.group_tasks[self.game_group_name] = asyncio.create_task(
                self.game_loop()
            )

        await self.save_and_broadcast_game_state()

    async def initialize_user(self):
        self.user_data = self.extract_user_data_from_jwt()
        if not self.user_data or not self.user_data.get("user_id"):
            await self.send_error_and_close("Invalid user data")
            return False
        return True

    def extract_user_data_from_jwt(self):
        user_data = {}
        headers = dict(self.scope["headers"])
        cookie_header = headers[b"cookie"]
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
        return user_data

    async def initialize_game_state(self):
        self.redis = redis.from_url("redis://redis:6379")

        self.game_id = await self.redis.get(f"user:{self.user_data['user_id']}:game")
        if not self.game_id:
            await self.send_error_and_close("User not registered in any game")
            return False
        self.game_id = int(self.game_id)

        game_data = await self.redis.get(f"game:{self.game_id}")
        if not game_data:
            await self.send_error_and_close("Game state not found")
            return False

        serializer = serializers.GameSerializer(data=json.loads(game_data))
        if not serializer.is_valid():
            print(serializer.errors)
            await self.send_error_and_close("Invalid game state")
            return False

        self.game_state = models.GameState.from_dict(serializer.validated_data)
        if not (await self.determine_user_role()):
            return False

        self.game_state.ball.x = self.field_width / 2
        self.game_state.ball.y = self.field_height / 2
        self.game_state.ball.dx = random.choice([-2, 2])
        self.game_state.ball.dy = random.choice([-2, 2])

        self.game_state.left.paddle_y = self.field_height / 2
        self.game_state.right.paddle_y = self.field_height / 2

        return True

    async def determine_user_role(self):
        if self.game_state.type == "computer":
            self.role = "left"
            self.game_state.left.player.connected = True
        elif self.game_state.type == "local":
            self.role = "both"
            self.game_state.left.player.connected = True
            self.game_state.right.player.connected = True
        elif self.game_state.type == "remote":
            if self.game_state.left.player.id == self.user_data["user_id"]:
                self.role = "left"
                self.game_state.left.player.connected = True
            elif self.game_state.right.player.id == self.user_data["user_id"]:
                self.role = "right"
                self.game_state.right.player.connected = True
            else:
                await self.send_error_and_close("User not part of the game")
                return False
        else:
            await self.send_error_and_close("Invalid game type")
            return False
        return True

    async def add_connection_to_group(self):
        self.game_group_name = f"game_{self.game_id}"
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)

    async def send_error_and_close(self, error_message):
        await self.send(text_data=json.dumps({"error": error_message}))
        await self.close()

    async def save_and_broadcast_game_state(self):
        await self.redis.set(
            f"game:{self.game_id}", json.dumps(self.game_state.to_dict())
        )
        await self.channel_layer.group_send(
            self.game_group_name,
            {"type": "game_state_update", "game_state": self.game_state.to_dict()},
        )

    async def game_state_update(self, event):
        serializer = serializers.GameSerializer(data=event["game_state"])
        if not serializer.is_valid():
            print(f"Errors: {serializer.errors}")
            return
        self.game_state = models.GameState.from_dict(serializer.validated_data)
        await self.send(
            text_data=json.dumps(
                {"type": "game_state_update", "game_state": serializer.validated_data}
            )
        )

    async def disconnect(self, close_code):
        # Abandonar el grupo de canales
        if not hasattr(self, "game_group_name"):
            return
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            event = json.loads(text_data)

            handlers = {"paddle_move": self.receive_paddle_update}

            if "type" in event:
                await handlers[event["type"]](event)

    async def receive_paddle_update(self, event):
        if not event.get("key"):
            return
        print(f"Received paddle update: {event}")
        if (
            event["key"] == "arrowUp" or event["key"] == "arrowDown"
        ) and self.role != "both":
            return
        direction_multiplier = (
            1 if (event["key"] == "arrowDown" or event["key"] == "s") else -1
        )
        print(f"Direction multiplier: {direction_multiplier}")
        if self.role == "left" or (
            self.role == "both" and (event["key"] == "w" or event["key"] == "s")
        ):
            self.game_state.left.paddle_y += (
                self.paddle_move_amount * direction_multiplier
            )
            print(f"Left paddle y: {self.game_state.left.paddle_y}")
        else:
            self.game_state.right.paddle_y += (
                self.paddle_move_amount * direction_multiplier
            )
            print(f"Right paddle y: {self.game_state.right.paddle_y}")

    def check_collisions(self):
        # Top and bottom walls
        if (
            self.game_state.ball.y - self.ball_radius <= 0
            or self.game_state.ball.y + self.ball_radius >= self.field_height
        ):
            self.game_state.ball.dy *= -1
            return

        # Left paddle
        if (
            self.game_state.ball.x - self.ball_radius <= self.paddle_width
            and self.game_state.ball.x - self.ball_radius > 0
            and not self.is_colliding
        ):
            if (
                self.game_state.ball.y
                >= self.game_state.left.paddle_y - self.paddle_height / 2
                and self.game_state.ball.y
                <= self.game_state.left.paddle_y + self.paddle_height / 2
            ):
                self.game_state.ball.dx *= -self.ball_speed_increment
                self.game_state.ball.dy *= self.ball_speed_increment
                self.is_colliding = True
                return

        # Right paddle
        if (
            self.game_state.ball.x + self.ball_radius
            >= self.field_width - self.paddle_width
            and self.game_state.ball.x + self.ball_radius < self.field_width
            and not self.is_colliding
        ):
            if (
                self.game_state.ball.y
                >= self.game_state.right.paddle_y - self.paddle_height / 2
                and self.game_state.ball.y
                <= self.game_state.right.paddle_y + self.paddle_height / 2
            ):
                self.game_state.ball.dx *= -self.ball_speed_increment
                self.game_state.ball.dy *= self.ball_speed_increment
                self.is_colliding = True
                return

        # Left and right walls
        if self.game_state.ball.x - self.ball_radius <= 0:
            self.game_state.left.score += 1
            self.game_state.ball.x = self.field_width / 2
            self.game_state.ball.y = self.field_height / 2
            self.game_state.ball.dx = -2
            self.game_state.ball.dy = random.choice([-2, 2])
            return
        if self.game_state.ball.x + self.ball_radius >= self.field_width:
            self.game_state.right.score += 1
            self.game_state.ball.x = self.field_width / 2
            self.game_state.ball.y = self.field_height / 2
            self.game_state.ball.dx = 2
            self.game_state.ball.dy = random.choice([-2, 2])
            return

        self.is_colliding = False

    async def game_loop(self):

        while True:
            # Mover la bola
            self.game_state.ball.x += self.game_state.ball.dx
            self.game_state.ball.y += self.game_state.ball.dy

            # Comprobar colisiones
            self.check_collisions()

            await self.save_and_broadcast_game_state()

            # Esperar 50ms antes de mover la bola nuevamente
            await asyncio.sleep(0.0166)

