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
        self,
        ball: Ball,
        left: Side,
        right: Side,
        winner_username: str,
        is_finished: int,
        start_countdown: int,
        next_side_to_collide: str,
    ):
        self.ball = ball
        self.left = left
        self.right = right
        self.winner_username = winner_username
        self.is_finished = is_finished
        self.start_countdown = start_countdown
        self.next_side_to_collide = next_side_to_collide

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Ball.from_dict(data["ball"]),
            Side.from_dict(data["left"]),
            Side.from_dict(data["right"]),
            data["winner_username"],
            data["is_finished"],
            data["start_countdown"],
            data["next_side_to_collide"],
        )

    def to_dict(self):
        return {
            "ball": self.ball.to_dict(),
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "winner_username": self.winner_username,
            "is_finished": self.is_finished,
            "start_countdown": self.start_countdown,
            "next_side_to_collide": self.next_side_to_collide,
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
    winner_id = models.IntegerField(null=True, blank=True)
    winner_username = models.CharField(max_length=100, null=True, blank=True)
    tournament_id = models.IntegerField(default=0)
    tree_index = models.IntegerField(default=0)
    rock_paper_scissors_id = models.IntegerField(null=True, blank=True)
    is_local_game = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class RockPaperScissorsGame(models.Model):
    left_player_id = models.IntegerField()
    left_player_username = models.CharField(max_length=100)
    left_player_choice = models.CharField(max_length=100, default="")
    right_player_id = models.IntegerField()
    right_player_username = models.CharField(max_length=100)
    right_player_choice = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    finished_at = models.DateTimeField(null=True, blank=True)
    winner_id = models.IntegerField(null=True, blank=True)
    winner_username = models.CharField(max_length=100, null=True, blank=True)
    tournament_id = models.IntegerField(default=0)
    tree_index = models.IntegerField(default=0)
    is_local_game = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
