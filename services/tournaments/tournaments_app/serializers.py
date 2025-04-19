from rest_framework import serializers
from .models import Tournament

class TournamentSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(format="%d %B %Y %H:%M", read_only=True)
    
    class Meta:
        model = Tournament
        fields = '__all__'


class UserTournamentStatsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    tournaments_played_count = serializers.IntegerField()
    tournaments_won_count = serializers.IntegerField()
    tournaments_played_names = serializers.ListField(child=serializers.CharField())
    tournaments_won_names = serializers.ListField(child=serializers.CharField())