from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Tournament
from .serializers import TournamentSerializer
import redis
from django.conf import settings
import json

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
	port=settings.REDIS_PORT,
	db=settings.REDIS_DB,
    decode_responses= True
)

@api_view(['POST'])
def create_tournament(request):
    print("entering create_tournament")
    print(request.data)
    serializer = TournamentSerializer(data=request.data)
    if serializer.is_valid():
        tournament = serializer.save()
        redis_client.publish('tournaments_channel', f'{tournament.id}')
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

@api_view(['POST'])
def join_tournament(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        # Aquí puedes agregar lógica para unir al usuario actual al torneo
        # Por ejemplo: tournament.players.add(request.user)
        redis_client.incr(f'tournament_{tournament.id}_player_count')
        redis_client.publish('tournaments_channel', json.dumps({
    	"tournamentId": tournament.id,
    	"user_count": redis_client.get(f'tournament_{tournament.id}_player_count')
}))
        return Response({"message": f"Te has unido al torneo '{tournament.name}'."}, status=status.HTTP_200_OK)
    except Tournament.DoesNotExist:
        return Response({"error": "Torneo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
