import json
from rest_framework import serializers
from game_app import models

    
class BallSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    dx = serializers.FloatField()
    dy = serializers.FloatField()

    
class PlayerSerializer(serializers.Serializer):
    is_human = serializers.BooleanField()
    id = serializers.IntegerField()
    connected = serializers.BooleanField()
    

class SideSerializer(serializers.Serializer):
    paddle_y = serializers.IntegerField()
    score = serializers.IntegerField()
    player = PlayerSerializer()

    
class GameStateSerializer(serializers.Serializer):
    type = serializers.CharField()
    is_paused = serializers.BooleanField()
    ball = BallSerializer()
    left = SideSerializer()
    right = SideSerializer()

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game
        fields = '__all__'

