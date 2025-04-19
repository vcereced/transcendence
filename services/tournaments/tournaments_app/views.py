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

def get_tournament_name(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return JsonResponse({"name": tournament.name, "is_active": tournament.is_active}, status=200)


class UserTournamentStatsAPIView(APIView):
    def get(self, request, user_id):
        if user_id == 0:
            return Response({"error": "Invalid user ID (0 is reserved for AI and you wont get this info)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = Participant.objects.get(user_id=user_id)
        except Participant.DoesNotExist:
            return Response(data = {
            "user_id": -1,
            "tournaments_played_count": 0,
            "tournaments_won_count": 0,
            "tournaments_played_names": [],
            "tournaments_won_names": [],
        }, status=status.HTTP_200_OK)

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

@api_view(['GET'])
def list_tournaments(request):
    
    tournaments = Tournament.objects.filter(is_active=True) #BE AWARE OF ADDING THE STATUS FIELD TO THE TOURNAMENT MODEL!
    serializer = TournamentSerializer(tournaments, many=True)
    return Response(serializer.data)



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
            "createdAt": tournament.created_at.strftime("%d %B %Y %H:%M"),
        }
        redis_client.publish('tournaments_channel', json.dumps(message))
        redis_client.set(f'tournament_{tournament.id}_player_count', 0)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("serializer.errors")
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        return Response({"message": f"Te has unido al torneo '{tournament.name}'."}, status=status.HTTP_200_OK)
    except Tournament.DoesNotExist:
        return Response({"error": "Torneo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_tournament_player_counts(request):
    keys = redis_client.scan_iter(match='tournament_*_player_count')
    tournament_counts = {}
    for key in keys:
        tournament_id = key.split('_')[1] 
        tournament_counts[tournament_id] = redis_client.get(key)
    return Response(tournament_counts, status=status.HTTP_200_OK)