from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tournament, Participant
from .serializers import TournamentSerializer, UserTournamentStatsSerializer
import redis
from django.conf import settings
import json
from .tasks import send_create_game_task
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
	port=settings.REDIS_PORT,
	db=settings.REDIS_DB,
    decode_responses= True
)

# API endpoint to get the name of a tournament by its ID the commented code is for the whole tournament

# @api_view(['GET']) 
# def get_tournament_name(request, tournament_id):
#     try:
#         tournament = Tournament.objects.get(id=tournament_id)
#         
#         serializer = TournamentSerializer(tournament)
#         return Response(serializer.data, status=200)
#     except Tournament.DoesNotExist:
#         return JsonResponse({"error": "Tournament not found"}, status=404)
def get_tournament_name(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return JsonResponse({"name": tournament.name}, status=200)

#ENDPOINT TO GET TOURNAMENTS PLAYED AND WON BY A USER BY ID
class UserTournamentStatsAPIView(APIView):
    def get(self, request, user_id):
        if user_id == 0:
            return Response({"error": "Invalid user ID (0 is reserved for AI and you wont get this info)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = Participant.objects.get(user_id=user_id)
        except Participant.DoesNotExist:
            return Response({"error": "Participant not found."}, status=status.HTTP_404_NOT_FOUND)

        tournaments_played = Tournament.objects.filter(participants=participant)
        tournaments_won = Tournament.objects.filter(champion=participant)

        data = {
            "user_id": user_id,
            "tournaments_played_count": tournaments_played.count(),
            "tournaments_won_count": tournaments_won.count(),
            "tournaments_played_names": [t.name for t in tournaments_played],
            "tournaments_won_names": [t.name for t in tournaments_won],
        }

        return Response(data, status=status.HTTP_200_OK)



################################################################################


@api_view(['POST'])
def create_tournament(request):
    print("entering create_tournament")
    print(request.data)
    serializer = TournamentSerializer(data=request.data)
    if serializer.is_valid():
        tournament = serializer.save()
        message = {
            "type": "tournament_created",
            "tournamentId": tournament.id,
            "tournamentName": tournament.name,
        }
        redis_client.publish('tournaments_channel', json.dumps(message))
        redis_client.set(f'tournament_{tournament.id}_player_count', 0)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("serializer.errors")
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_tournaments(request):
    tournaments = Tournament.objects.all()
    serializer = TournamentSerializer(tournaments, many=True)
    return Response(serializer.data)

# Prepare this for allowing users to join a tournament, be aware
# of the edge cases like the tournament not existing or the user already being in the tournament.
# or the tournament being full. TAKE CARE OF THIS !!!
@api_view(['POST'])
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        # redis_client.incr(f'tournament_{tournament.id}_player_count')
        # redis_client.publish('tournaments_channel', json.dumps({
    	# "tournamentId": tournament.id,
    	# "user_count": redis_client.get(f'tournament_{tournament.id}_player_count')}))
        #This is for testing sending tasks to the game service
        # send_create_game_task(players)
        return Response({"message": f"Te has unido al torneo '{tournament.name}'."}, status=status.HTTP_200_OK)
    except Tournament.DoesNotExist:
        return Response({"error": "Torneo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_tournament_player_counts(request):
    keys = redis_client.scan_iter(match='tournament_*_player_count')
    tournament_counts = {}
    for key in keys:
        tournament_id = key.split('_')[1]  # Extraer el ID del torneo de la clave
        tournament_counts[tournament_id] = redis_client.get(key)
    return Response(tournament_counts, status=status.HTTP_200_OK)