from django.http import HttpResponse
from django.shortcuts import render
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import RegisterSerializer, UserSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
import jwt
import os
from .models import CustomUser, EmailOTPDevice, Friendship  # Importa tu modelo personalizado
from auth_app.utils.utilsToptDevice import genTOPTDevice, activateTOPTDevice, verifyTOPTDevice, CustomError
from auth_app.utils.utils import verifyEmailTOPTDevice, verifyUser, verifyPendingUser

from rest_framework import generics

SECRET_KEY = os.getenv("JWT_SECRET")

@api_view(['POST'])
def resend_otp_view(request):
	
	email = request.data.get("email")

	try:
		if not email:
			return Response({"error": "not received username."}, status=status.HTTP_400_BAD_REQUEST)
		
		user = CustomUser.objects.get(email=email)

		if user is None:
			return Response({"error": "user not in bbdd (resend_otp_view_view)."}, status=status.HTTP_400_BAD_REQUEST)
		
		device = EmailOTPDevice.objects.get(user=user)
		device.generate_otp()
		device.send_otp()

		return Response({ 'message': 'OTP EMAIL reenviado otra vez' }, status=status.HTTP_200_OK)
	
	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "OTP Wrong."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register_view(request):

	serializer = RegisterSerializer(data=request.data)

	if serializer.is_valid():
		user = serializer.save()
		user.is_active = False  # Desactivamos la cuenta hasta que confirme el OTP
		user.save()
		device, _ = EmailOTPDevice.objects.get_or_create(user=user)
		device.generate_otp()
		device.send_otp()
		return Response({ "message" : "User register OK. Go to EMAIL to confirm!!." }, status=status.HTTP_201_CREATED)
	
	elif verifyPendingUser(request.data.get("email"), request.data.get("username"), request.data.get("password")) == 'ok':
		user = CustomUser.objects.get(email=request.data.get("email"))
		device, _ = EmailOTPDevice.objects.get_or_create(user=user)
		device.generate_otp()
		device.send_otp()
		return Response({ "message" : "User register OK. Go to EMAIL to confirm!!." }, status=status.HTTP_201_CREATED)
	
	elif verifyPendingUser(request.data.get("email"), request.data.get("username"), request.data.get("password")) == 'password wrong' and CustomUser.objects.get(email=request.data.get("email")).is_active == False:
		return Response({ "error"	: "wrong password" }, status=status.HTTP_400_BAD_REQUEST)
	
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_email_otp_register_view(request):

	otp_token = request.data.get('otp_token')
	email = request.data.get('email')

	try:
		if not email or not otp_token:
			return Response({"error": "not received email or otp."}, status=status.HTTP_400_BAD_REQUEST)
		
		user = CustomUser.objects.get(email=email)

		if user is None:
			return Response({"error": "user not in bbdd (verify_email_otp_view)."}, status=status.HTTP_400_BAD_REQUEST)
		
		if verifyEmailTOPTDevice(email, otp_token):
			user.is_active = True
			user.save()
			return Response({ 'message': 'OTP EMAIL verificado con éxito',}, status=status.HTTP_200_OK)
	
	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "OTP Wrong."}, status=status.HTTP_400_BAD_REQUEST)
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api_view(request):

	email = request.data.get('email')
	password = request.data.get('password')

	if verifyUser(email, password) != 'ok':
		return Response({"error": verifyUser(email, password)}, status=status.HTTP_400_BAD_REQUEST)
		
	else:
		user = CustomUser.objects.get(email=email)

	#refreshToken = RefreshToken.for_user(user)
	#refreshToken['email'] = user.email

	device = EmailOTPDevice.objects.get(user=user)
	device.generate_otp()
	device.send_otp()

	return Response({
		'username': user.username, 
		'message': 'introduce el otp enviado al e-mail.'
	}, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_email_otp_login_view(request):

	email = request.data.get('email')
	#password = request.data.get('password')
	otp_token = request.data.get('otp_token')

	try:
		user = CustomUser.objects.get(email=email, is_active = True)

		#if not user.check_password(password):
		#	return Response({"error": "password wrong."}, status=status.HTTP_400_BAD_REQUEST)
		
		if verifyEmailTOPTDevice(email, otp_token):

			refresh = RefreshToken.for_user(user)
			refresh['username'] = user.username

			return Response({
				'message': 'OTP EMAIL LOGED',
				'refresh': str(refresh),
				'access': str(refresh.access_token)
			}, status=status.HTTP_200_OK)

	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "OTP WRONG."}, status=status.HTTP_400_BAD_REQUEST)
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def validate_token_view(request):

    token = request.COOKIES.get('accessToken')

    if not token:
        return Response({"error": "accessToken is required in cookies"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return Response(status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)

    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def refresh_token_view(request):

	refresh_token = request.data.get('refresh_token')

	if not refresh_token:
		return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

	try:
		token = RefreshToken(refresh_token)
		new_access_token = str(token.access_token)

		return Response({
            'access_token': new_access_token,
        }, status=status.HTTP_200_OK)
    
	except TokenError as e:
		return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
	
@api_view(['POST'])
def updateName_view(request):
	
	email = request.data.get("email")
	newUsername = request.data.get("newUsername")

	if not email or not newUsername:
		return Response({"error": "Faltan datos en el request"}, status=status.HTTP_400_BAD_REQUEST)
	
	if CustomUser.objects.filter(username=newUsername).exists():
		return Response({"error": "El nombre de usuario ya está en uso"}, status=status.HTTP_400_BAD_REQUEST)

	try:
		user = CustomUser.objects.get(email=email)

		user.username = newUsername
		user.save()
		return Response({'message': 'username changed succesfully'}, status=status.HTTP_200_OK)

	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(["POST"])
def updatePassword_view(request):
    email = request.data.get("email")
    old_password = request.data.get("oldPassword")
    new_password = request.data.get("newPassword")

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Autenticar al usuario con la contraseña antigua
    if not user.check_password(old_password):
        return Response({"error": "La contraseña actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar la contraseña
    user.set_password(new_password)
    user.save()

    return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)

@api_view(["POST"])
def updatePictureUrl_view(request):

	email = request.data.get("email")
	src = request.data.get("src")

	try:
		user = CustomUser.objects.get(email=email)
		user.profile_picture = src
		user.save()
	except CustomUser.DoesNotExist:
		return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

	return Response({"message": "picture_url cambiada correctamente."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def playersList_view(request):
    players = CustomUser.objects.values('username', 'profile_picture')
    return Response(players)

@api_view(['POST'])
def dataUser_view(request):
	username = request.data.get("username")
	email = request.data.get("email")

	try:
		if not email and username:
			user = CustomUser.objects.get(username=username)
		elif email and not username:
			user = CustomUser.objects.get(email=email)
		else:
			return Response({"error": "missing username or email"}, status=status.HTTP_400_BAD_REQUEST)

	except CustomUser.DoesNotExist:
		return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return Response({"message": "data extrated succesfully", "username": user.username, "picture_url": user.profile_picture}, status=status.HTTP_200_OK)

@api_view(['POST'])
def isFriendShip_view(request):
	username1 = request.data.get("username1")
	username2 = request.data.get("username2")
							  
	if not username1 or not username2:
		return Response({"error": "missing a username"}, status=status.HTTP_400_BAD_REQUEST)
	
	if Friendship.are_friends(username1, username2):
		return Response({"message": "Are friends"}, status=status.HTTP_200_OK)
	else:
		return Response({"message": "Are not friends"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def friendShip_view(request, action):
	username1 = request.data.get('username1')
	username2 = request.data.get('username2')
	print("debugeo= ", username1, ", ", username2)
	if not username1 or not username2:
		return Response({"error": "Missing username1 or username2"}, status=400)

	if action == 'add':
		print("entra en add")
		# Añadir amigos
		if not Friendship.are_friends(username1, username2):
			Friendship.add_friend(username1, username2)
			return Response({"message": "Son amigos"}, status=200)
		else:
			return Response({"error": "They are already friends or the usernames are the same"}, status=200)
    
	elif action == 'remove':
		print("entra en remove")
		# Eliminar amigos
		if Friendship.remove_friend(username1, username2):
			return Response({"message": "Ya no son amigos"}, status=200)
		else:
			return Response({"error": "They are not friends or no valid relationship exists"}, status=200)
	
	return Response({"error": "Invalid action"}, status=400)


class UserDetail(generics.RetrieveAPIView):
	queryset = CustomUser.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'username'
