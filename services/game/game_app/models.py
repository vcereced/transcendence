from django.db import models


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


class Side:
    def __init__(self, paddle_y: int, score: int):
        self.paddle_y = paddle_y
        self.score = score

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["paddle_y"], data["score"])
    
    def to_dict(self):
        return {
            "paddle_y": self.paddle_y,
            "score": self.score,
        }


class GameState:
    def __init__(
        self, ball: Ball, left: Side, right: Side
    ):
        self.ball = ball
        self.left = left
        self.right = right

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Ball.from_dict(data["ball"]),
            Side.from_dict(data["left"]),
            Side.from_dict(data["right"]),
        )
    
    def to_dict(self):
        return {
            "ball": self.ball.to_dict(),
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }
    

class Game(models.Model):
    left_player_id = models.IntegerField()
    left_player_username = models.CharField(max_length=100)
    left_player_score = models.IntegerField(default=0)
    right_player_id = models.IntegerField()
    tournament_id = models.IntegerField(default=0)
    game_id = models.CharField(max_length=100, default="")
    right_player_username = models.CharField(max_length=100)
    right_player_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    finished_at = models.DateTimeField(null=True, blank=True)
    return_url = models.URLField(max_length=200, default="")

    class Meta:
        ordering = ["-created_at"]

