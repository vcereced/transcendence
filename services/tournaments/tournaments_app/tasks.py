# services/tournaments/tournaments_app/tasks.py

from celery import shared_task
from celery import Celery
from django.conf import settings
import redis

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
	port=settings.REDIS_PORT,
	db=settings.REDIS_DB,
    decode_responses= True
)

# Conexión a Celery
app = Celery('tournaments_project', broker='amqp://guest:guest@message-broker:5672//')

# Definir una tarea que envía otra tarea a otro servicio
@shared_task
def send_create_game_task(players):
    """
    Esta tarea se ejecuta en el servicio 'tournaments', y cuando se ejecuta, envía una tarea
    a otro servicio para crear un juego.
    """
    # Crear el mensaje que queremos enviar
    message = {
        "left_player_id": players["left_player_id"],
        "left_player_username": players["left_player_username"],
        "right_player_id": players["right_player_id"],
        "right_player_username": players["right_player_username"],
    }

    # Enviar la tarea al servicio 'game' (asumiendo que la tarea se llama 'create_game')
    app.send_task(
        'create_game', 
        args=[message], 
        queue='game_tasks')

    print("Tarea enviada al servicio de juegos.")


# This task will receive the request from websocket service to start the matchmaking
@shared_task(name='start_matchmaking')
def start_matchmaking(message):
   
    print(f"Comenzando emparejamiento de jugadores para el torneo {message['tournament_id']}.")

    # print the message
    print(message)
    #obtain the tournament id
    tournament_id = message['tournament_id']
    #obtain the tournament user list from redis
    user_list =  redis_client.smembers(f"tournament_{tournament_id}_users")
    print ("User list:")
    print(user_list)
    print("Emparejamiento de jugadores completado.")