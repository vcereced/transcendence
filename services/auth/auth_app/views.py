from django.http import HttpResponse
from django.shortcuts import render
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import RegisterSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import jwt
import os
from .models import CustomUser, EmailOTPDevice  # Importa tu modelo personalizado
from auth_app.utils.utils import genTOPTDevice, activateTOPTDevice, verifyTOPTDevice, CustomError
from django.utils.timezone import now, timedelta


SECRET_KEY = os.getenv("JWT_SECRET")

@api_view(['POST'])
def register_view(request):
	message = None
	qr_base64 = None

	serializer = RegisterSerializer(data=request.data)
	if serializer.is_valid():
		user = serializer.save()
		user.is_active = False  # Desactivamos la cuenta hasta que confirme el OTP
		user.save()

		if user.auth_method == "None":
			message = "User register OK, without 2FA, go to login"
			user.is_active = True
               
		elif user.auth_method == "Qr":
			message = "User register OK. Scan QR to set 2FA."
			qr_base64 = genTOPTDevice(user)
		elif user.auth_method == "Email":
			message = "User register OK. Go to EMAIL to confirm!!."
			device, _ = EmailOTPDevice.objects.get_or_create(user=user)
			device.generate_otp()
			device.send_otp()

		return Response({
			"auth_method" 	: user.auth_method,
			"message"		: message,
			"qr_code"		: qr_base64,  # Enviar QR en base64 para mostrar en frontend
		}, status=status.HTTP_201_CREATED)

	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_email_otp_view(request):
	username = request.data.get('username')
	otp_token = request.data.get('otp_token')

	try:
		user = CustomUser.objects.get(username=username)
		if user is None:
			return Response({"error": "usuario no guardado en bbdd (verify_email_otp_view)."}, status=status.HTTP_400_BAD_REQUEST)
		
		print("user: ", user, "otp_email: ", otp_token)
		device = EmailOTPDevice.objects.get(user=user, otp_token=otp_token)

		if device.valid_until < now():
			return Response({"error": "El código ha expirado."}, status=status.HTTP_400_BAD_REQUEST)

		user.is_active = True
			
		return Response({
			'message': 'OTP EMAIL verificado con éxito',

		}, status=status.HTTP_200_OK)

	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "Email Device doesnt exist."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_otp_view(request):
	username = request.data.get("username")
	otp_token = request.data.get("otp_token")
	
	try:
		if not username or not otp_token:
			return Response({"error": "not found username or otp."}, status=status.HTTP_400_BAD_REQUEST)

		user = CustomUser.objects.get(username=username)

		if user is None:
			return Response({"error": "usuario no guardado en bbdd (verify_otp_view)."}, status=status.HTTP_400_BAD_REQUEST)


		if activateTOPTDevice(user, otp_token):
			user.is_active = True  # Activamos la cuenta
			user.save()
			return Response({"message": "OTP OK. User active, go to login."}, status=status.HTTP_200_OK)
		else:
			return Response({"error": "Código OTP wrong."}, status=status.HTTP_400_BAD_REQUEST)

	except CustomError.DoesNotExist:
		return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)

	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login_api_view(request):

	username = request.data.get('username')
	password = request.data.get('password')
	otp_token = request.data.get('otp_token')

	#user = authenticate(username=username, password=password)
      
	user = CustomUser.objects.filter(username=username).first()  # Buscar el usuario directamente

	if user is None or user.check_password(password) is False:  # Verificar la contraseña manualmente
		return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

	#if user is None:
	#	return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

	refresh = RefreshToken.for_user(user)
	refresh['username'] = user.username

	if user.auth_method == "None":
		return Response({            
			'message': 'Login OK premooooo.',
			'auth_method' : user.auth_method,
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}, status=status.HTTP_200_OK)

	elif user.auth_method == "Qr":
		try:
			verifyTOPTDevice(user, otp_token)

			return Response({
				'message': 'Inicio de sesión exitoso.',
                'auth_method' : user.auth_method,
				'refresh': str(refresh),
				'access': str(refresh.access_token)
			}, status=status.HTTP_200_OK)
			
		except CustomError as e:
			return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)







@api_view(['GET'])
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