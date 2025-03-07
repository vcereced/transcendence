import jwt
from django.db.models import Q

from game_app.models import Game, RockPaperScissorsGame

def extract_user_data_from_jwt(headers_raw):
	user_data = {}
	headers = dict(headers_raw)
	cookie_header = headers[b"cookie"]
	if cookie_header:
		for c in cookie_header.decode().split(";"):
			if "accessToken" in c:
				jwt_token = c.split("=")[1]
				try:
					payload = jwt.decode(
						jwt_token, options={"verify_signature": False}
					)
					user_data["username"] = payload.get("username")
					user_data["user_id"] = payload.get("user_id")
				except jwt.DecodeError as e:
					print(f"Error decoding token: {e}")
				break
	return user_data

def query_for_active_game(user_id):
	active_game_data = {"has_active_pong_game": False, "has_active_rps_game": False}
	error = {"error": "Multiple active games found"}
	try:
		game = Game.objects.get(
			(
				Q(left_player_id=user_id)
				| Q(right_player_id=user_id)
			)
			& Q(is_finished=False)
		)
	except Game.MultipleObjectsReturned:
		return error
	except Game.DoesNotExist:
		game = None

	try:
		rps_game = RockPaperScissorsGame.objects.get(
			Q(player_1_id=user_id) | Q(player_2_id=user_id)
			& Q(is_finished=False)
		)
	except RockPaperScissorsGame.MultipleObjectsReturned:
		return error
	except RockPaperScissorsGame.DoesNotExist:
		rps_game = None

	if rps_game:
		active_game_data["has_active_rps_game"] = True
	elif game:
		active_game_data["has_active_pong_game"] = True
	
	return active_game_data


