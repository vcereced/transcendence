import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as redis

class RoomConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		print("Connecting to WebSocket")
		user = self.scope['user']
		print(user)
		# Obtiene el nombre de la sala desde la URL
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = f'room_{self.room_name}'

		# Conectar a Redis usando el nombre del servicio en Docker
		self.redis = redis.from_url("redis://redis:6379")  # Cambiado de localhost a redis
		
		# Define la clave de conteo de usuarios
		self.user_count_key = f"{self.room_group_name}_user_count"

		# Añade el canal del cliente a la sala
		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		# Incrementa el contador de usuarios y envía actualización
		await self.redis.incr(self.user_count_key)
		await self.update_user_count()

		# Acepta la conexión WebSocket
		await self.accept()

	async def disconnect(self, close_code):
		# Quita el canal del cliente de la sala
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

		# Disminuir el contador de usuarios en Redis
		await self.redis.decr(self.user_count_key)

		# Envia el número actualizado de usuarios conectados en la sala después de desconectar
		await self.update_user_count()

	async def receive(self, text_data):
		# Maneja los mensajes recibidos y retransmite el mensaje a todos en el grupo de la sala
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat_message',
				'message': message
			}
		)

	async def chat_message(self, event):
		# Envía el mensaje a WebSocket
		message = event['message']
		await self.send(text_data=json.dumps({
			'message': message
		}))
	
	async def update_user_count(self):
		# Obtener el número actualizado de usuarios conectados
		current_user_count = await self.redis.get(self.user_count_key)
		
		# Envia el número actualizado de usuarios conectados al grupo
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'user_count',
				'count': int(current_user_count) if current_user_count is not None else 0
			}
		)
	
	async def user_count(self, event):
		# Recibe el número de usuarios conectados en la sala y envíalo al WebSocket
		count = event['count']
		await self.send(text_data=json.dumps({
			'user_count': count
		}))
 