import json
import django
from redis import asyncio as redis
import os
import random
import asyncio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game.settings")
django.setup()

from game_app import serializers
from game import settings as s
from game_app.models import GameState


async def discover_games():
    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
    while True:
        discovered_game = await redis_client.lpop("game_queue")
        if not discovered_game:
            await asyncio.sleep(1)
            continue
        await asyncio.sleep(0.1) # Small delay to allow the game state to be created in redis
        asyncio.create_task(play_game(discovered_game))
        print(f"Game discovered: {discovered_game}")


async def play_game(game_name):
    redis_client = redis.Redis(host="redis", port=6379)

    game_state = await load_game_state(redis_client, game_name)

    while game_state.left.score < 5 and game_state.right.score < 5:
        async with redis_client.pipeline() as pipe:
            while True:
                try:
                    # Make sure we are the only ones updating the game state
                    await pipe.watch(f"{game_name}")

                    game_state = await load_game_state(pipe, game_name)

                    game_state = check_collisions(game_state)

                    game_state.ball.x += game_state.ball.dx
                    game_state.ball.y += game_state.ball.dy

                    # now we can put the pipeline back into buffered mode with MULTI
                    pipe.multi()
                    await save_game_state(pipe, game_name, game_state)
                    await pipe.execute()
                    break
                except redis.WatchError:
                    # Retry if someone else modified the game state
                    continue
        await asyncio.sleep(1 / s.FPS)


async def load_game_state(redis_client, game_name):
    game_state_data = await redis_client.get(f"{game_name}")
    if game_state_data:
        game_state_serializer = serializers.GameStateSerializer(
            data=json.loads(game_state_data)
        )
        if game_state_serializer.is_valid():
            return GameState.from_dict(game_state_serializer.validated_data)
        else:
            raise Exception(f"Invalid game state: {game_state_serializer.errors}")
    else:
        raise Exception("Game state not found")


async def save_game_state(redis_client, game_name, game_state):
    await redis_client.set(f"{game_name}", json.dumps(game_state.to_dict()))


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
        s.PADDLE_WIDTH,
        game_state.left.paddle_y,
        bounce_away_direction=1,
    )

    # Right paddle
    game_state = check_paddle_collision(
        game_state,
        s.FIELD_WIDTH - s.PADDLE_WIDTH,
        game_state.right.paddle_y,
        bounce_away_direction=-1,
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
    game_state: GameState, paddle_x_position, paddle_y_position, bounce_away_direction
):
    ball_left_border = game_state.ball.x - s.BALL_RADIUS
    ball_right_border = game_state.ball.x + s.BALL_RADIUS
    ball_top_border = game_state.ball.y - s.BALL_RADIUS
    ball_bottom_border = game_state.ball.y + s.BALL_RADIUS
    paddle_top_border = paddle_y_position - s.PADDLE_HEIGHT / 2
    paddle_bottom_border = paddle_y_position + s.PADDLE_HEIGHT / 2

    # If the ball is moving away from the paddle, it has already collided
    if bounce_away_direction * game_state.ball.dx > 0:
        return game_state

    # If the ball is not within the paddle's x position, it can't collide
    if not (
        ball_left_border <= paddle_x_position and ball_right_border >= paddle_x_position
    ):
        return game_state

    if (
        ball_top_border <= paddle_bottom_border
        and ball_bottom_border >= paddle_top_border
    ):
        game_state.ball.dx *= -s.BALL_SPEED_INCREMENT
        game_state.ball.dy *= s.BALL_SPEED_INCREMENT

    return game_state


if __name__ == "__main__":
    asyncio.run(discover_games())
