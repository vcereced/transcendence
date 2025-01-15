from django.db import models
import json


# Custom models for the game that work with redis instead of a database
class Ball:
    def __init__(self, x: float, y: float, dx: float, dy: float):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["x"], data["y"], data["dx"], data["dy"])

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "dx": self.dx,
            "dy": self.dy,
        }


class Player:
    def __init__(self, is_human: bool, id: int, connected: bool):
        self.is_human = is_human
        self.id = id
        self.connected = connected

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["is_human"], data["id"], data["connected"])

    def to_dict(self):
        return {
            "is_human": self.is_human,
            "id": self.id,
            "connected": self.connected,
        }


class Side:
    def __init__(self, paddle_y: int, score: int, player: Player):
        self.paddle_y = paddle_y
        self.score = score
        self.player = player

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["paddle_y"], data["score"], Player.from_dict(data["player"]))
    
    def to_dict(self):
        return {
            "paddle_y": self.paddle_y,
            "score": self.score,
            "player": self.player.to_dict(),
        }


class GameState:
    def __init__(
        self, game_type: str, is_paused: bool, ball: Ball, left: Side, right: Side
    ):
        self.type = game_type
        self.is_paused = is_paused
        self.ball = ball
        self.left = left
        self.right = right

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["type"],
            data["is_paused"],
            Ball.from_dict(data["ball"]),
            Side.from_dict(data["left"]),
            Side.from_dict(data["right"]),
        )
    
    def to_dict(self):
        return {
            "type": self.type,
            "is_paused": self.is_paused,
            "ball": self.ball.to_dict(),
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }
    

class Game(models.Model):
    left_player_id = models.IntegerField()
    left_player_username = models.CharField(max_length=100)
    left_player_score = models.IntegerField(default=0)
    right_player_id = models.IntegerField()
    right_player_username = models.CharField(max_length=100)
    right_player_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

