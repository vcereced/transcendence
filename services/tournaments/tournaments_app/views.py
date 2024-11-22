from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Tournament
from .serializers import TournamentSerializer

@api_view(['POST'])
def create_tournament(request):
    print("entering create_tournament")
    print(request.data)
    serializer = TournamentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
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
        return Response({"message": f"Te has unido al torneo '{tournament.name}'."}, status=status.HTTP_200_OK)
    except Tournament.DoesNotExist:
        return Response({"error": "Torneo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
