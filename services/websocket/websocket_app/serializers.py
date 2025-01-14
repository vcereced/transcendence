import json
from rest_framework import serializers

    
class BallSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    dx = serializers.IntegerField()
    dy = serializers.IntegerField()

    
class PlayerSerializer(serializers.Serializer):
    is_human = serializers.BooleanField()
    id = serializers.IntegerField()
    connected = serializers.BooleanField()
    

class SideSerializer(serializers.Serializer):
    paddle_y = serializers.IntegerField()
    score = serializers.IntegerField()
    player = PlayerSerializer()

    
class GameSerializer(serializers.Serializer):
    type = serializers.CharField()
    is_paused = serializers.BooleanField()
    ball = BallSerializer()
    left = SideSerializer()
    right = SideSerializer()

    

