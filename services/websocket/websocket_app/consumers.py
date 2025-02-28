import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis
import asyncio
import jwt
from .tasks import send_start_matchmaking_task, end_game_simulation
from .redis_manager import RedisManager 



class TournamentCounterConsumer(AsyncWebsocketConsumer):
    """Maneja la conexión de WebSocket global para los torneos."""

    async def connect(self):
        """Conecta al WebSocket global y se suscribe al canal de Redis."""
        print("Connecting to global WebSocket")

        self.redis_manager = RedisManager()  # Instanciamos RedisManager
        self.room_group_name = "global_tournament_counter"

        # Suscribirse al canal de Redis
        self.pubsub = await self.redis_manager.subscribe("tournaments_channel")

        # Añadir el canal del WebSocket al grupo de Django
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Aceptar la conexión WebSocket
        await self.accept()

        # Iniciar el bucle para escuchar los mensajes de Redis
        asyncio.create_task(self.listen_to_redis())

    async def listen_to_redis(self):
        """Escucha los mensajes de Redis y envía actualizaciones de conteo."""
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message["data"])
                if data["type"] == "user_count_update":
                    await self.send(json.dumps({
                        "tournament_id": data.get("tournament_id"),
                        "user_count": data.get("user_count")
                    }))
            await asyncio.sleep(0.042)

    async def disconnect(self, close_code):
        """Maneja la desconexión y limpia el WebSocket."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def update_user_count(self, tournament_id, user_count):
        """Envía una actualización de conteo de jugadores al grupo global."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "tournament_user_count",
                "tournament_id": tournament_id,
                "user_count": user_count,
            },
        )

    async def tournament_user_count(self, event):
        """Recibe actualizaciones del contador de jugadores desde Redis."""
        await self.send(json.dumps({
            "tournament_id": event["tournament_id"],
            "user_count": event["user_count"]
        }))


class RoomConsumer(AsyncWebsocketConsumer):
    """Maneja la conexión de WebSocket para un torneo específico."""

    # ============================
    #           WebSocket Connect
    # ============================

    async def connect(self):
        """Conecta el WebSocket de un torneo específico y maneja la conexión del usuario."""
        print("Connecting to specific tournament WebSocket")
        self.user = self.scope.get("user")

        # Obtener el nombre del torneo desde la URL
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"tournament_{self.room_name}"

        self.redis_manager = RedisManager()  # Instanciamos RedisManager
        self.user_count_key = f"{self.room_group_name}_player_count"

        # Añadir el canal al grupo del torneo
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Incrementar el contador de jugadores en Redis
        current_user_count = await self.redis_manager.incr_value(self.user_count_key)

        # Publicar actualización en Redis (para el consumidor global)
        await self.publish_global_update(current_user_count)

        # Extraer información del usuario desde el JWT
        await self.extract_user_info()

        # Almacenar información del usuario en Redis
        await self.redis_manager.set_value(f"user_channel:{self.username}", self.channel_name)
        
        # Añadir el usuario al set de usuarios en el torneo
        await self.redis_manager.add_user_to_tournament(self.room_group_name, self.username, self.user_id)

        # Publicar actualización en el torneo
        await self.publish_local_update()

        # Enviar un mensaje de bienvenida
        await self.send_message(f"Hello from the server, {self.username}")

        # Aceptar la conexión WebSocket
        await self.accept()

        # Simulación de fin de juego (solo para pruebas)
        # if current_user_count == 4:
        #     message = {
        #         "tournament_id": self.room_name,
        #         "winner": "jugador1dg",
        #         "loser": "jugador2dg",
        #         "tree_id": "1",
        #         "type": "game_end"
        #     }
        #     end_game_simulation(message)

        asyncio.create_task(self.listen_to_game_end())

    # ============================
    #           WebSocket Disconnect
    # ============================

    async def disconnect(self, close_code):
        """Maneja la desconexión de un usuario."""
        print(f"User {self.username} disconnected")
        await self.redis_manager.remove_user_from_tournament(self.room_group_name, self.username)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.publish_local_update()

        # Disminuir el contador de jugadores
        current_user_count = await self.redis_manager.decr_value(self.user_count_key)
        await self.publish_global_update(current_user_count)

    # ============================
    #           Data Publication
    # ============================

    async def publish_global_update(self, user_count):
        """Publica la actualización de conteo en el canal de Redis global."""
        message = {
            "type": "user_count_update",
            "tournament_id": self.room_name,
            "user_count": user_count,
        }
        await self.redis_manager.publish("tournaments_channel", message)

    async def publish_local_update(self):
        """Publica actualización de la lista de usuarios en el canal de Redis local."""
        user_list = await self.redis_manager.get_tournament_users(self.room_group_name)
        message = {
            "type": "user_list",
            "tournament_id": self.room_name,
            "user_list": user_list
        }
        await self.redis_manager.publish(self.room_group_name, message)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "user_list", "user_list": user_list}
        )

    # ============================
    #           Message Handlers
    # ============================

    async def user_list(self, event):
        """Maneja el mensaje de tipo 'user_list'."""
        await self.send(json.dumps({"type": "user_list", "user_list": event["user_list"]}))

    async def send_message(self, message):
        """Envía un mensaje directo a un usuario."""
        channel_name = await self.redis_manager.get_value(f"user_channel:{self.username}")
        if channel_name:
            await self.channel_layer.send(
                channel_name,
                {"type": "direct_message", "message": message},
            )

    async def direct_message(self, event):
        """Maneja mensajes directos a usuarios."""
        await self.send(json.dumps({"message": event["message"]}))

    async def game_end_notification(self, event):
        """Envía una notificación cuando termina un juego."""
        await self.send(json.dumps({
            "type": "game_end",
            "tournament_id": event["tournament_id"],
            "winner": event["winner"],
            "loser": event["loser"],
            "match_id": event["tree_id"],
            "username": self.username
        }))

    # ============================
    #           Game End Listener
    # ============================

    async def listen_to_game_end(self):
        """Escucha eventos de fin de juego en Redis."""
        pubsub = await self.redis_manager.subscribe(self.room_group_name)
        print(f"Listening to game end events in {self.room_group_name}")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message["data"])
                if data["type"] == "game_end":
                    print(f"\033[91m {data} <- data GAME END \033[0m")
                    await self.game_end_notification(data)

            await asyncio.sleep(0.042)

    # ============================
    #           Helper Methods
    # ============================

    async def extract_user_info(self):
        """Extrae información del usuario desde el JWT en las cookies."""
        headers = dict(self.scope["headers"])
        cookie_header = headers.get(b"cookie", b"")

        if cookie_header:
            for c in cookie_header.decode().split(";"):
                if "accessToken" in c:
                    jwt_token = c.split("=")[1]
                    try:
                        payload = jwt.decode(jwt_token, options={"verify_signature": False})
                        self.username = payload.get("username")
                        self.user_id = payload.get("user_id")
                        print(f"User connected: {self.username} (ID: {self.user_id})")
                    except jwt.DecodeError as e:
                        print(f"Error decoding token: {e}")
                    break

    async def receive(self, text_data):
        """Maneja los mensajes entrantes del frontend."""
        data = json.loads(text_data)
        message_type = data.get("type")
        print(f"\033[91m Received message type: {message_type} \033[0m")

        if message_type == "start_tournament":
            print("\033[92mRecibido evento para iniciar torneo\033[0m")
            message = {"tournament_id": self.room_name}
            send_start_matchmaking_task(message)

            # Esperar a que se cree el árbol del torneo en Redis
            tournament_tree_key = f"tournament_{self.room_name}_tree"
            for _ in range(50):
                key_type = await self.redis_manager.redis.type(tournament_tree_key)
                if key_type == b'hash':
                    break
                await asyncio.sleep(0.1)

            # Obtener el árbol del torneo
            tournament_tree = await self.redis_manager.redis.hgetall(tournament_tree_key)
            tournament_tree = {k.decode("utf-8"): v.decode("utf-8") for k, v in tournament_tree.items()}

            print(f"\033[31mEl árbol del torneo es: {tournament_tree}\033[0m")

            # Enviar el mensaje a todos los jugadores
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "start_tournament",
                    "message": "Tournament is starting",
                    "tournament_tree": tournament_tree,
                },
            )

    async def start_tournament(self, event):
        """Inicia el torneo y envía la notificación a los jugadores."""
        message = event["message"]
        tournament_tree = event["tournament_tree"]
        await self.send(text_data=json.dumps({"type": "start_tournament", "message": message, "tournament_tree": tournament_tree}))
