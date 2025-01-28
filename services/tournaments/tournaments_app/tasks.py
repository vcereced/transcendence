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
# @shared_task
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
# @shared_task(name='start_matchmaking')
# def start_matchmaking(message):
   
#     print(f"Comenzando emparejamiento de jugadores para el torneo {message['tournament_id']}.")

#     # print the message
#     print(message)
#     #obtain the tournament id
#     tournament_id = message['tournament_id']
#     #obtain the tournament user list from redis
#     user_list =  redis_client.smembers(f"tournament_{tournament_id}_users")
#     print ("User list:")
#     print(user_list)
#     print("Emparejamiento de jugadores completado.")

@shared_task(name='start_matchmaking')
def start_matchmaking(message):
    """
    Empareja jugadores para un torneo y envía tareas para crear juegos 1vs1.
    Si hay menos de 8 jugadores, completa con usuarios ficticios.
    """
    print(f"Comenzando emparejamiento de jugadores paraa el torneo {message['tournament_id']}.")

    # Obtener el ID del torneo
    tournament_id = message['tournament_id']

    # Obtener la lista de usuarios del torneo desde Redis
    user_list = redis_client.smembers(f"tournament_{tournament_id}_users")
    print("User list:")
    print(user_list)

    # Procesar la lista para extraer username y user_id
    players = []
    for user_entry in user_list:
        try:
            username, user_id = user_entry.split(": ")
            players.append({"username": username, "user_id": int(user_id)})
        except ValueError as e:
            print(f"Error al procesar la entrada de usuario: {user_entry}. Detalles: {e}")

    # Completar la lista si hay menos de 8 jugadores
    if len(players) < 8:
        print("Jugadores insuficientes. Agregando jugadores ficticios para completar.")
        current_id = 691  # ID inicial para los usuarios ficticios
        for i in range(len(players) + 1, 9):  # Rellenar hasta tener 8 jugadores
            players.append({
                "username": f"IA{i}",
                "user_id": current_id
            })
            current_id += 1
        print(f"Lista completada con jugadores ficticios: {players}")

    # Emparejar jugadores en formato 1vs1
    pairs = []
    for i in range(0, len(players) - 1, 2):  # Tomar pares consecutivos
        left_player = players[i]
        right_player = players[i + 1]
        pairs.append({
            "left_player_id": left_player["user_id"],
            "left_player_username": left_player["username"],
            "right_player_id": right_player["user_id"],
            "right_player_username": right_player["username"],
        })

    print(f"Emparejamiento completado. Pairs: {pairs}")

    # Enviar una tarea para cada par al servicio de creación de juegos
    for pair in pairs:
        print(f"Enviando tarea para par: {pair}")
        send_create_game_task(pair) 

    print("Tareas de creación de juegos enviadas para todos los pares.")
