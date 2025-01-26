from celery import shared_task
from celery import Celery

app = Celery('websocket_project', broker='amqp://guest:guest@rabbitmq:5672//')

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