# services/tournaments/tournaments_app/tasks.py

from celery import shared_task
from celery import Celery
from django.conf import settings
import redis
import json

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
	port=settings.REDIS_PORT,
	db=settings.REDIS_DB,
    decode_responses= True
)

# Conexión a Celery
app = Celery('tournaments_project', broker='amqp://guest:guest@message-broker:5672//')

# This is not a Celery task, but a helper function to send a task to the 'game' service
def send_create_game_task(players):
    message = {
        "left_player_id": players["left_player_id"],
        "left_player_username": players["left_player_username"],
        "right_player_id": players["right_player_id"],
        "right_player_username": players["right_player_username"],
        "tournament_id": players["tournament_id"],
        "tree_id": players["tree_id"],
    }

    app.send_task(
        'create_game', 
        args=[message], 
        queue='game_tasks')

    print("Tarea enviada al servicio de juegos.")

###########################################################
#                   TOURNAMENT LOGIC
###########################################################

def start_next_round(tournament_id, round_id, winners):
    """
    Genera los emparejamientos de la siguiente ronda y los guarda en Redis.
    """
    next_round_id = str(int(round_id) + 1)  # Pasamos a la siguiente ronda
    tournament_tree_key = f"tournament_{tournament_id}_tree"

    # Si solo queda un ganador, significa que el torneo ha terminado
    if len(winners) == 1:
        print(f"🏆 ¡Torneo {tournament_id} finalizado! Campeón: {winners[0]}")
        return  

    # Generar la nueva lista de partidos
    new_round_matches = []
    for i in range(0, len(winners) - 1, 2):
        match = {
            "tree_id": str(i + 5) if round_id == "1" else "7",
            "players": {
                "left": {"id": winners[i], "username": f"Jugador_{winners[i]}"},
                "right": {"id": winners[i + 1], "username": f"Jugador_{winners[i + 1]}"},
            },
            "winner": None,
            "loser": None,
            "status": "pending"
        }
        new_round_matches.append(match)

    # Guardar la nueva ronda en Redis
    redis_client.hset(tournament_tree_key, f"round_{next_round_id}", json.dumps(new_round_matches))

    print(f"🔥 Iniciando ronda {next_round_id} con emparejamientos: {new_round_matches}")

    # Enviar las nuevas partidas a `game`
    for match in new_round_matches:
        send_create_game_task({
            "left_player_id": match["players"]["left"]["id"],
            "left_player_username": match["players"]["left"]["username"],
            "right_player_id": match["players"]["right"]["id"],
            "right_player_username": match["players"]["right"]["username"],
            "tournament_id": tournament_id,
            "tree_id": match["tree_id"]
        })


def update_tournament_tree(tournament_id, tree_id, winner):
    """
    Guarda el resultado de un partido en la estructura del torneo en Redis.
    Si la ronda está completa, inicia la siguiente ronda.
    """
    tournament_tree_key = f"tournament_{tournament_id}_tree"

    # Determinar la ronda actual según el tree_id
    round_number = "1" if tree_id in ["1", "2", "3", "4"] else "2" if tree_id in ["5", "6"] else "3"
    round_key = f"round_{round_number}"

    # Obtener la lista de partidos de la ronda
    current_round = redis_client.hget(tournament_tree_key, round_key)
    current_round = json.loads(current_round) if current_round else []

    # Buscar el partido correspondiente al tree_id y actualizarlo
    for match in current_round:
        if match["tree_id"] == tree_id:
            match["winner"] = winner
            match["loser"] = match["players"]["left"]["id"] if match["players"]["right"]["id"] == winner else match["players"]["right"]["id"]
            match["status"] = "completed"
            break  

    # Guardar la actualización en Redis
    redis_client.hset(tournament_tree_key, round_key, json.dumps(current_round))
    
    print(f"🔄 Árbol actualizado en {round_key}: {current_round}")

    # Verificar si ya todos los partidos de la ronda han terminado
    completed_games = [match for match in current_round if match["status"] == "completed"]
    total_games = len(current_round)

    if len(completed_games) == total_games:
        print(f"Todos los partidos de la Ronda {round_number} han terminado.")
        start_next_round(tournament_id, round_number, [match["winner"] for match in completed_games])


#THIS IS JUST IN CASE WE NEED IT. IT RETURNS THE TOURNAMENT HISTORY
def get_tournament_history(tournament_id):
    """
    Recupera toda la información del torneo desde Redis.
    """
    tournament_tree_key = f"tournament_{tournament_id}_tree"
    tournament_data = {}

    # Obtener todas las rondas almacenadas en Redis
    for round_key in redis_client.hkeys(tournament_tree_key):
        round_matches = redis_client.hget(tournament_tree_key, round_key)
        tournament_data[round_key] = json.loads(round_matches) if round_matches else []

    print(f" Historial del torneo {tournament_id}: {json.dumps(tournament_data, indent=4)}")
    return tournament_data

###########################################################
#                   CELERY TASKS
###########################################################

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

    # THIS IS THE MATCHMAKING ALGORITHM IT SHOULD BE REPLACED BY A BETTER ONE
    pairs = []
    for i in range(0, len(players) - 1, 2):  # Tomar pares consecutivos
        left_player = players[i]
        right_player = players[i + 1]
        pairs.append({
            "left_player_id": left_player["user_id"],
            "left_player_username": left_player["username"],
            "right_player_id": right_player["user_id"],
            "right_player_username": right_player["username"],
            "tournament_id": tournament_id,
            "tree_id": f"{(i // 2) + 1}", 
            # "return_url": message["return_url"],
        })

    print(f"Emparejamiento completado. Pairs: {pairs}")
    # Generar el árbol del torneo en Redis
    # Formato: {round_1: [{tree_id: 1, left_player: "user1", right_player: "user2", winner: None}, ...]}
    tournament_tree_key = f"tournament_{tournament_id}_tree"
    first_round = [
        {
            "tree_id": pair["tree_id"],
            "left_player": pair["left_player_username"],
            "right_player": pair["right_player_username"],
            "winner": None
        }
        for pair in pairs
    ]
    #This is the whole tournament tree
    redis_client.hset(tournament_tree_key, "round_1", json.dumps(first_round))
    
    print("\033[33m" + f"🏆 Árbol del torneo inicializado en Redis: {first_round}" + "\033[0m")


    # Enviar una tarea para cada par al servicio de creación de juegos
    for pair in pairs:
        print(f"Enviando tarea para par: {pair}")
        send_create_game_task(pair) 

    print("Tareas de creación de juegos enviadas para todos los pares.")

@shared_task(name='game_end')
def game_end(message):
    message_redis = {
        "type": "game_end",
        "winner": message["winner"],
        "loser": message["loser"],
        "tournament_id": message["tournament_id"],
        "tree_id":   message["tree_id"],
    }
    channel = f"tournament_{message['tournament_id']}"
    print(f"El juego ha terminado. Ganador: {message['winner']}.")
    print("\033[31m" + "Fin del juego." + "\033[0m")
    redis_client.publish(channel, json.dumps(message_redis))
    # Aquí se puede agregar lógica adicional, como actualizar las puntuaciones de los jugadores.
    update_tournament_tree(message["tournament_id"], message["tree_id"], message["winner"])
    # Por ahora, simplemente imprimimos un mensaje.
    #imprimir en rojo