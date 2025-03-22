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


import uuid
import time

def acquire_lock(lock_key, timeout=5):
    """
    Intenta obtener el lock.
    Si no puede, espera hasta un máximo de 'timeout' segundos.
    Si obtiene el lock, devuelve un ID único del lock.
    """
    lock_id = str(uuid.uuid4())  # Generar un ID único para el lock
    end = time.time() + timeout  # Tiempo de expiración de la espera
    print(f"Intentando obtener lock {lock_key} con ID {lock_id}")
    while time.time() < end:
        # Intentamos obtener el lock (NX significa "solo si no existe")
        if redis_client.set(lock_key, lock_id, nx=True, ex=timeout):
            print(f"Lock {lock_key} obtenido con ID {lock_id}")
            return lock_id  # Si lo conseguimos, devolvemos el lock ID
        time.sleep(0.1)  # Esperamos un poco antes de volver a intentarlo
    return None  # Si no conseguimos el lock en el tiempo especificado, retornamos None

def release_lock(lock_key, lock_id):
    """
    Libera el lock solo si el lock ID coincide con el actual.
    """
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    redis_client.eval(script, 1, lock_key, lock_id)  # Ejecutamos el script Lua para liberar el lock
    print(f"Lock {lock_key} liberado con ID {lock_id}")

# This is not a Celery task, but a helper function to send a task to the 'game' service
def send_create_game_task(players):
    message = {
        "left_player_id": players["left_player_id"],
        "left_player_username": players["left_player_username"],
        "right_player_id": players["right_player_id"],
        "right_player_username": players["right_player_username"],
        "tournament_id": players["tournament_id"],
        "tree_index": players["tree_id"],
    }

    app.send_task(
        'create_game', 
        args=[message], 
        queue='game_tasks')

    print("Tarea enviada al servicio de juegos.")

###########################################################
#                   TOURNAMENT LOGIC
###########################################################

# def start_next_round(tournament_id, round_id, winners):
#     """
#     Genera los emparejamientos de la siguiente ronda y los guarda en Redis.
#     """
#     next_round_id = str(int(round_id) + 1)  # Pasamos a la siguiente ronda
#     tournament_tree_key = f"tournament_{tournament_id}_tree"
#     #PRint en AZUL
#     print("\033[34m" + f" Iniciando ronda {next_round_id} con ganadores: {winners}" + "\033[0m")
#     # Si solo queda un ganador, significa que el torneo ha terminado
#     if len(winners) == 1:
#         print(f"🏆 ¡Torneo {tournament_id} finalizado! Campeón: {winners[0]}")
#         return  

#     # Generar la nueva lista de partidos
#     new_round_matches = []
#     for i in range(0, len(winners) - 1, 2):
#         match = {
#             "tree_id": str(i + 5) if round_id == "1" else "7",
#             "players": {
#                 "left": {"id": winners[i], "username": f"{winners[i]}"},
#                 "right": {"id": winners[i + 1], "username": f"{winners[i + 1]}"},
#             },
#             "winner": None,
#             "loser": None,
#             "status": "pending"
#         }
#         new_round_matches.append(match)

#     # Guardar la nueva ronda en Redisz  
#     redis_client.hset(tournament_tree_key, f"round_{next_round_id}", json.dumps(new_round_matches))

#     print(f"Iniciando ronda {next_round_id} con emparejamientos: {new_round_matches}")

#     # Enviar las nuevas partidas a `game`
#     for match in new_round_matches:
#         send_create_game_task({
#             "left_player_id": match["players"]["left"]["id"],
#             "left_player_username": match["players"]["left"]["username"],
#             "right_player_id": match["players"]["right"]["id"],
#             "right_player_username": match["players"]["right"]["username"],
#             "tournament_id": tournament_id,
#             "tree_id": match["tree_id"]
#         })

def start_next_round(tournament_id, round_id, winners):
    
    next_round_id = str(int(round_id) + 1)  # Pasamos a la siguiente ronda
    tournament_tree_key = f"tournament_{tournament_id}_tree"
    print(f"Iniciando ronda {next_round_id} con ganadores: {winners}")

    if len(winners) == 1:
        print(f"🏆 ¡Torneo {tournament_id} finalizado! Campeón: {winners[0]}")
        return  

    # Obtener el último tree_id utilizado
    last_round_key = f"round_{round_id}"
    last_round_matches = redis_client.hget(tournament_tree_key, last_round_key)
    last_round_matches = json.loads(last_round_matches) if last_round_matches else []
    
    if last_round_matches:
        last_tree_id = max(int(match["tree_id"]) for match in last_round_matches)
    else:
        last_tree_id = 0  # Si no hay partidos previos, empezamos desde 1

    new_round_matches = []
    next_tree_id = last_tree_id + 1  # Comenzar desde el siguiente disponible

    for i in range(0, len(winners) - 1, 2):
        match = {
            "tree_id": str(next_tree_id),
            "players": {
                "left": {"id": winners[i], "username": f"{winners[i]}"},
                "right": {"id": winners[i + 1], "username": f"{winners[i + 1]}"},
            },
            "winner": None,
            "loser": None,
            "status": "pending"
        }
        new_round_matches.append(match)
        next_tree_id += 1  # Incrementamos para el siguiente partido

    redis_client.hset(tournament_tree_key, f"round_{next_round_id}", json.dumps(new_round_matches))
    print(f"Iniciando ronda {next_round_id} con emparejamientos: {new_round_matches}")

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
    Guarda el resultado de un partido en Redis y avanza a la siguiente ronda si es necesario.
    """
    lock_key = f"lock:tournament:{tournament_id}"  # Clave para el lock
    lock_id = acquire_lock(lock_key)  # Intentamos obtener el lock

    if not lock_id:
        print("No se pudo obtener el lock, omitiendo actualización.")
        return  # Si no conseguimos el lock, terminamos la función sin hacer nada

    try:
        # Ahora que tenemos el lock, podemos hacer las modificaciones en el árbol del torneo
        print("\033[31m" + f"Actualizando árbol del torneo {tournament_id} para el partido {tree_id}" + "\033[0m")
        tournament_tree_key = f"tournament_{tournament_id}_tree"
        round_number = "1" if str(tree_id) in ["1", "2", "3", "4"] else "2" if str(tree_id) in ["5", "6"] else "3"
        print(f"Round number: {round_number}")
        round_key = f"round_{round_number}"
        print(f"Round key: {round_key}")
        current_round = redis_client.hget(tournament_tree_key, round_key)
        current_round = json.loads(current_round) if current_round else []

        for match in current_round:
            print(f"Match: {match}")
            if match["tree_id"] == str(tree_id):
                match["winner"] = winner
                match["loser"] = match["players"]["left"]["username"] if match["players"]["right"]["username"] == winner else match["players"]["right"]["username"]
                loser = match["players"]["left"]["username"] if match["players"]["right"]["username"] == winner else match["players"]["right"]["username"]
                print("\033[32m" + f"🏆 Ganador del partido {tree_id}: {winner}. Perdedor: {loser}" + "\033[0m")
                match["status"] = "completed"
                break

        redis_client.hset(tournament_tree_key, round_key, json.dumps(current_round))
        print(f"🔄 Árbol actualizado en {round_key}: {current_round}")

        # Si todos los partidos de la ronda han terminado, iniciar la siguiente ronda
        completed_games = [match for match in current_round if match["status"] == "completed"]
        print(f"Partidos completados: {len(completed_games)} de {len(current_round)}")
        if len(completed_games) == len(current_round):
            start_next_round(tournament_id, round_number, [match["winner"] for match in completed_games])
    finally:
        release_lock(lock_key, lock_id)  # Liberamos el lock después de terminar la operación


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
        "players": {  
            "left": {"id": pair["left_player_id"], "username": pair["left_player_username"]},
            "right": {"id": pair["right_player_id"], "username": pair["right_player_username"]},
        },
        "winner": None,
        "loser": None,
        "status": "pending"
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

# @shared_task(name='game_end')
# def game_end(message):
#     message_redis = {
#         "type": "game_end",
#         "winner": message["winner"],
#         "loser": message["loser"],
#         "tournament_id": message["tournament_id"],
#         "tree_id":   message["tree_id"],
#     }
#     channel = f"tournament_{message['tournament_id']}"
#     print(f"El juego ha terminado. Ganador: {message['winner']}.")
#     print("\033[31m" + "Fin del juego." + "\033[0m")
#     redis_client.publish(channel, json.dumps(message_redis))
#     # Aquí se puede agregar lógica adicional, como actualizar las puntuaciones de los jugadores.
#     update_tournament_tree(message["tournament_id"], message["tree_id"], message["winner"])
@shared_task(name='game_end')
def game_end(message):
    """
    Maneja la finalización de un juego, publicando el evento en Redis
    y actualizando el árbol del torneo.
    """
    print(f"El juego ha terminado. Ganador: {message['winner']}.")
    print("\033[31m" + "Fin del juego." + "\033[0m")
    print(f"Mensaje recibido en game_end task: {message}")
    # Publicar en Redis el mensaje de finalización del juego
    channel = f"tournament_{message['tournament_id']}"
    redis_client.publish(channel, json.dumps({
        "type": "game_end",
        "winner": message["winner"],
        "loser": message["loser"],
        "tournament_id": message["tournament_id"],
        "tree_id": message["tree_index"],
    }))

    # Llamar a la función que actualiza el torneo
    update_tournament_tree(message["tournament_id"], message["tree_index"], message["winner"])


