# services/tournaments/tournaments_app/tasks.py

from celery import shared_task
from celery import Celery

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


# Definir una tarea que recibe un mensaje y comiemza el emparejamiento de jugadores
@shared_task
def start_matchmaking(message):
    """
    Esta tarea se ejecuta en el servicio 'tournaments', y cuando se ejecuta, comienza el emparejamiento
    de jugadores para un torneo.
    """
    print(f"Comenzando emparejamiento de jugadores para el torneo {message['tournament_id']}.")

    # Lógica de emparejamiento de jugadores aquí

    print("Emparejamiento de jugadores completado.")