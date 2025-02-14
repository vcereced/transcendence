from celery import shared_task
from celery import Celery

app = Celery('websocket_project', broker='amqp://guest:guest@message-broker:5672//')

#This task sends a message to the matchmaking service to start the matchmaking process

@shared_task
def send_start_matchmaking_task(message):
   
    app.send_task(
        'start_matchmaking',
        args=[message],
        queue='matchmaking_tasks')

    print("Tarea  start Matchmaking enviada al servicio de torneos.")


#THIS IS JUST A SIMULATION OF THE END GAME TASK, this call should be done
#when the game ends, at game service.
@shared_task
def end_game_simulation(message):
   
    # Enviar la tarea al servicio 'tournaments' (asumiendo que la tarea se llama 'end_game_simulation')
    app.send_task(
        'game_end',
        args=[message],
        queue='matchmaking_tasks')

    print("Tarea end_game_simulation enviada al servicio de juegos.")