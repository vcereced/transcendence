import json
from rest_framework import serializers
from game_app import models

    
class BallSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    dx = serializers.FloatField()
    dy = serializers.FloatField()
    

class SideSerializer(serializers.Serializer):
    paddle_y = serializers.FloatField()
    score = serializers.IntegerField()

    
class GameStateSerializer(serializers.Serializer):
    ball = BallSerializer()
    left = SideSerializer()
    right = SideSerializer()

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game
        fields = '__all__'

class RockPaperScissorsGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RockPaperScissorsGame
        fields = '__all__'

