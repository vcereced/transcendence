import json
import django
from redis import asyncio as redis
import os
import random
import asyncio
from asgiref.sync import sync_to_async
import math
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")
django.setup()

from game_app import serializers
from game import settings as s
from game_app.models import GameState, Game, Ball


async def discover_games():
    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
    while True:
        discovered_game_id = await redis_client.lpop("game_queue")
        if not discovered_game_id:
            await asyncio.sleep(1)
            continue
        await asyncio.sleep(
            0.1
        )  # Small delay to allow the game state to be created in redis
        asyncio.create_task(play_game(int(discovered_game_id)))
        print(f"Game discovered: {discovered_game_id}")


async def play_game(game_id: int):
    redis_client = redis.Redis(host="redis", port=6379)

    game = await query_db_for_game(game_id)

    async with asyncio.TaskGroup() as tg:
        if game.left_player_id == 0:
            tg.create_task(control_paddle_by_computer(game_id, "left"))
        elif game.right_player_id == 0:
            tg.create_task(control_paddle_by_computer(game_id, "right"))

        game_state = await load_game_state(redis_client, game_id)

        while game_state.left.score < 500 and game_state.right.score < 500:
            game_state = await load_game_state(redis_client, game_id)
            game_state = check_collisions(game_state)
            game_state.ball.x += game_state.ball.dx
            game_state.ball.y += game_state.ball.dy
            await save_game_state(redis_client, game_id, game_state)
            await asyncio.sleep(1 / s.FPS)


@sync_to_async
def query_db_for_game(game_id):
    return Game.objects.get(pk=game_id)


async def control_paddle_by_computer(game_id, side):
    redis_client = redis.Redis(host="redis", port=6379)
    final_paddle_y = 0
    target_paddle_y = 0
    last_seen_ball = Ball(
        s.INITIAL_GAME_STATE["ball"]["x"], s.INITIAL_GAME_STATE["ball"]["y"], 0, 0
    )
    last_seen_time = time.time()
    refresh_rate = 1
    while True:
        game_state = await load_game_state(redis_client, game_id)

        if side == "left":
            final_paddle_y = game_state.left.paddle_y
        elif side == "right":
            final_paddle_y = game_state.right.paddle_y

        # Refresh the last seen ball position every refresh_rate seconds
        if time.time() - last_seen_time <= refresh_rate:
            last_seen_time = time.time()
            last_seen_ball = game_state.ball
            target_paddle_y = determine_target_paddle_y(last_seen_ball)

        final_paddle_y = approach_target_paddle_y(final_paddle_y, target_paddle_y)

        await redis_client.set(
            f"game:{game_id}:{side}_paddle_y", json.dumps(final_paddle_y)
        )
        await asyncio.sleep(1 / s.FPS)


def determine_target_paddle_y(last_seen_ball : Ball):
    return last_seen_ball.y

def approach_target_paddle_y(final_paddle_y, target_paddle_y):
    if final_paddle_y < target_paddle_y - s.PADDLE_MOVE_AMOUNT:
        final_paddle_y += s.PADDLE_MOVE_AMOUNT
    elif final_paddle_y > target_paddle_y + s.PADDLE_MOVE_AMOUNT:
        final_paddle_y -= s.PADDLE_MOVE_AMOUNT
    final_paddle_y = max(
        s.PADDLE_HEIGHT / 2,
        min(s.FIELD_HEIGHT - s.PADDLE_HEIGHT / 2, final_paddle_y),
    )

    return final_paddle_y


async def load_game_state(redis_client: redis.Redis, game_id):
    ball_data = await redis_client.get(f"game:{game_id}:ball")
    left_paddle_data = await redis_client.get(f"game:{game_id}:left_paddle_y")
    right_paddle_data = await redis_client.get(f"game:{game_id}:right_paddle_y")
    scores_data = await redis_client.get(f"game:{game_id}:scores")
    if ball_data and left_paddle_data and right_paddle_data and scores_data:
        scores = json.loads(scores_data)
        game_state_data = {
            "ball": json.loads(ball_data),
            "left": {"paddle_y": json.loads(left_paddle_data), "score": scores["left"]},
            "right": {
                "paddle_y": json.loads(right_paddle_data),
                "score": scores["right"],
            },
        }
        game_state_serializer = serializers.GameStateSerializer(data=game_state_data)
        if game_state_serializer.is_valid():
            return GameState.from_dict(game_state_serializer.validated_data)
        else:
            raise Exception(f"Invalid game state: {game_state_serializer.errors}")
    else:
        raise Exception("Game state not found")


async def save_game_state(redis_client: redis.Redis, game_id, game_state: GameState):
    await redis_client.set(
        f"game:{game_id}:ball", json.dumps(game_state.ball.to_dict())
    )
    await redis_client.set(
        f"game:{game_id}:scores",
        json.dumps({"left": game_state.left.score, "right": game_state.right.score}),
    )


def check_collisions(game_state: GameState):
    # Top and bottom walls
    if (
        game_state.ball.y - s.BALL_RADIUS <= 0
        or game_state.ball.y + s.BALL_RADIUS >= s.FIELD_HEIGHT
    ):
        game_state.ball.dy *= -1
        return game_state

    # Left paddle
    game_state = check_paddle_collision(
        game_state,
        -s.PADDLE_OFFSET,
        game_state.left.paddle_y,
        1,
    )

    # Right paddle
    game_state = check_paddle_collision(
        game_state,
        s.FIELD_WIDTH + s.PADDLE_OFFSET,
        game_state.right.paddle_y,
        -1,
    )

    # Left wall
    if game_state.ball.x <= 0:
        game_state.right.score += 1
        game_state.ball.x = s.FIELD_WIDTH / 2
        game_state.ball.y = s.FIELD_HEIGHT / 2
        game_state.ball.dx = s.INITIAL_BALL_SPEED  # Serve to the right
        game_state.ball.dy = random.choice([-1, 1]) * s.INITIAL_BALL_SPEED
        return game_state

    # Right wall
    if game_state.ball.x >= s.FIELD_WIDTH:
        game_state.left.score += 1
        game_state.ball.x = s.FIELD_WIDTH / 2
        game_state.ball.y = s.FIELD_HEIGHT / 2
        game_state.ball.dx = -s.INITIAL_BALL_SPEED  # Serve to the left
        game_state.ball.dy = random.choice([-1, 1]) * s.INITIAL_BALL_SPEED
        return game_state

    return game_state


def check_paddle_collision(
    game_state: GameState,
    paddle_center_x_position,
    paddle_center_y_position,
    bounce_away_direction,
):
    # If the ball is not moving towards the paddle, no collision
    if game_state.ball.dx * bounce_away_direction > 0:
        return game_state

    centers_distance = math.sqrt(
        (game_state.ball.x - paddle_center_x_position) ** 2
        + (game_state.ball.y - paddle_center_y_position) ** 2
    )

    # If the ball is not close enough to the paddle, no collision
    if centers_distance > s.BALL_RADIUS + s.PADDLE_RADIUS:
        return game_state

    # Bounce the ball away from the paddle
    collision_angle = math.atan2(
        game_state.ball.y - paddle_center_y_position,
        game_state.ball.x - paddle_center_x_position,
    )
    initial_angle = math.atan2(game_state.ball.dy, game_state.ball.dx)
    theta = math.pi + collision_angle - initial_angle
    final_angle = collision_angle + theta
    initial_magnitude = math.sqrt(game_state.ball.dx**2 + game_state.ball.dy**2)
    final_magnitude = initial_magnitude * s.BALL_SPEED_INCREMENT
    game_state.ball.dx = final_magnitude * math.cos(final_angle)
    game_state.ball.dy = final_magnitude * math.sin(final_angle)

    if abs(game_state.ball.dx) < s.MINIMUM_X_SPEED:
        game_state.ball.dx = (
            s.MINIMUM_X_SPEED if game_state.ball.dx > 0 else -s.MINIMUM_X_SPEED
        )

    return game_state


if __name__ == "__main__":
    asyncio.run(discover_games())
