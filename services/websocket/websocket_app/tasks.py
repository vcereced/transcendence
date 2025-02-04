from celery import shared_task
from celery import Celery

app = Celery('websocket_project', broker='amqp://guest:guest@message-broker:5672//')

@shared_task
def send_start_matchmaking_task(message):
    """
    Esta tarea se ejecuta en el servicio 'websocket', y cuando se ejecuta, envía una tarea
    a otro servicio para comenzar el emparejamiento de jugadores.
    """
    # Enviar la tarea al servicio 'tournaments' (asumiendo que la tarea se llama 'start_matchmaking')
    app.send_task(
        'start_matchmaking',
        args=[message],
        queue='matchmaking_tasks')

    print("Tarea  start Matchmaking enviada al servicio de torneos.")

@shared_task
def end_game_simulation(message):
    """
    Esta tarea se ejecuta en el servicio 'websocket', y cuando se ejecuta, envía una tarea
    a otro servicio para finalizar la simulación de un juego.
    """
    # Enviar la tarea al servicio 'tournaments' (asumiendo que la tarea se llama 'end_game_simulation')
    app.send_task(
        'end_match',
        args=[message],
        queue='matchmaking_tasks')

    print("Tarea end_game_simulation enviada al servicio de juegos.")