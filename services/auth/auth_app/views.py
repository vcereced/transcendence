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
from auth_app.utils.utilsToptDevice import genTOPTDevice, activateTOPTDevice, verifyTOPTDevice, CustomError
from auth_app.utils.utils import verifyEmailTOPTDevice, verifyUser

SECRET_KEY = os.getenv("JWT_SECRET")



@api_view(['POST'])
def register_view(request):
	qr_base64 = None

	serializer = RegisterSerializer(data=request.data)

	print("debugeo====", request.data.get("username"), request.data.get("password"))
	if serializer.is_valid():
		user = serializer.save()
		user.is_active = False  # Desactivamos la cuenta hasta que confirme el OTP
		user.save()

		if user.auth_method == "None":
			message = "User register OK, without 2FA, go to login"
			user.is_active = True
			user.save()
		elif user.auth_method == "Qr":
			message = "User register OK. Scan QR to set 2FA."
			qr_base64 = genTOPTDevice(user)
		elif user.auth_method == "Email":
			message = "User register OK. Go to EMAIL to confirm!!."
			device, _ = EmailOTPDevice.objects.get_or_create(user=user)
			device.generate_otp()
			device.send_otp()

		return Response({
			"message"		: message,
			"auth_method" 	: user.auth_method,
			"qr_code"		: qr_base64,  # Enviar QR en base64 para mostrar en frontend
		}, status=status.HTTP_201_CREATED)
	
	elif CustomUser.objects.filter(username=request.data.get("username")).first().is_active == False and CustomUser.objects.filter(username=request.data.get("username")).first().email == request.data.get("email"):

		print("entrooooo")
		user = CustomUser.objects.get(username=request.data.get("username"))

		if user.auth_method == "None":
			message = "User register OK, without 2FA, go to login"
			user.is_active = True
			user.save()
		elif user.auth_method == "Qr":
			message = "User register OK. Scan QR to set 2FA."
			qr_base64 = genTOPTDevice(user)
		elif user.auth_method == "Email":
			message = "User register OK. Go to EMAIL to confirm!!."
			device, _ = EmailOTPDevice.objects.get_or_create(user=user)
			device.generate_otp()
			device.send_otp()

		return Response({
			"message"		: message,
			"auth_method" 	: user.auth_method,
			"qr_code"		: qr_base64,  # Enviar QR en base64 para mostrar en frontend
		}, status=status.HTTP_201_CREATED)
	
	#elif CustomUser.objects.filter(username=request.data.get("username")).first().email != request.data.get("email"):
	#	return Response({"error": "email wrong"}, status=status.HTTP_400_BAD_REQUEST)

	else:
		#return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({"error": verifyUser(request.data.get("username"), request.data.get("password"))}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp_view(request):
	username = request.data.get("username")
	otp_token = request.data.get("otp_token")
	password = request.data.get('password')

	try:
		if not username or not otp_token:
			return Response({"error": "not received username or otp."}, status=status.HTTP_400_BAD_REQUEST)

		user = CustomUser.objects.get(username=username)

		if user is None:
			return Response({"error": "user not in bbdd (verify_otp_view)."}, status=status.HTTP_400_BAD_REQUEST)

		if activateTOPTDevice(user, otp_token):
			user.password = password  
			user.is_active = True  # Activate the account
			user.save()
			return Response({"message": "OTP OK. User active, go to login."}, status=status.HTTP_200_OK)
		else:
			return Response({"error": "Código OTP wrong."}, status=status.HTTP_400_BAD_REQUEST)

	except CustomError.DoesNotExist:
		return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)
	
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_email_otp_view(request):
	username = request.data.get('username')
	otp_token = request.data.get('otp_token')
	password = request.data.get('password')

	try:
		if not username or not otp_token:
			return Response({"error": "not received username or otp."}, status=status.HTTP_400_BAD_REQUEST)
		
		user = CustomUser.objects.get(username=username)

		if user is None:
			return Response({"error": "user not in bbdd (verify_email_otp_view)."}, status=status.HTTP_400_BAD_REQUEST)
		
		if verifyEmailTOPTDevice(user, otp_token):
			print("debugeooooo== ", request.data.get('password'))
			user.password = password  
			user.is_active = True
			user.save()

			return Response({
			'message': 'OTP EMAIL verificado con éxito',
			}, status=status.HTTP_200_OK)
	
	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "OTP Wrong."}, status=status.HTTP_400_BAD_REQUEST)
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api_view(request):

	username = request.data.get('username')
	password = request.data.get('password')

	print("login api view username, password ", username, password)

	if verifyUser(username, password) != 'ok':
		print("EEEERRRROORRR")
		return Response({"error": verifyUser(username, password)}, status=status.HTTP_400_BAD_REQUEST)
		
	else:
		user = CustomUser.objects.get(username=username)

	refreshToken = RefreshToken.for_user(user)
	refreshToken['username'] = user.username
	refresh = None,
	access = None
	
	if user.auth_method == "None":
          
		message = 'Login OK premooooo.',
		auth_method = user.auth_method,
		refresh = str(refreshToken),
		access = str(refreshToken.access_token)
		
	elif user.auth_method == "Qr":

		message = 'introduce el otp con app authentificatooor.',
		auth_method = user.auth_method,

	elif user.auth_method == "Email":
		device = EmailOTPDevice.objects.get(user=user)
		device.generate_otp()
		device.send_otp()

		message = 'introduce el otp enviado al e-mail.',
		auth_method = user.auth_method,

	return Response({            
			'message': message,
			'auth_method' : auth_method,
			'refresh': refresh,
			'access': access
		}, status=status.HTTP_200_OK)

@api_view(['POST'])
def login_qr_view(request):

	username = request.data.get('username')
	password = request.data.get('password')
	otp_token = request.data.get('otp_token')

	user = CustomUser.objects.get(username=username) 

	if user is None or user.check_password(password) is False:  
		return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

	try:
        # Descomentar para activar 2FA. LO DEJAMOS COMENTADO PARA NO TENER QUE INGRESAR EL OTP CADA VEZ QUE QUERAMOS INICIAR SESIÓN
		# verifyTOPTDevice(user, otp_token) 

		refresh = RefreshToken.for_user(user)
		refresh['username'] = user.username

		return Response({
			'message': 'QR OTP validado. LOGED',
			'auth_method' : user.auth_method,
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}, status=status.HTTP_200_OK)
		
	except CustomError as e:
		return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_email_view(request):

	username = request.data.get('username')
	password = request.data.get('password')
	otp_token = request.data.get('otp_token')

	try:
		user = CustomUser.objects.get(username=username, is_active = True)

		if user.password != password:
			return Response({"error": "password wrong."}, status=status.HTTP_400_BAD_REQUEST)
		
		if verifyEmailTOPTDevice(user, otp_token):

			refresh = RefreshToken.for_user(user)
			refresh['username'] = user.username

			return Response({
				'message': 'OTP EMAIL LOGED',
				'auth_method' : user.auth_method,
				'refresh': str(refresh),
				'access': str(refresh.access_token)
			}, status=status.HTTP_200_OK)

	except (CustomUser.DoesNotExist):
		return Response({"error": "User no exist."}, status=status.HTTP_400_BAD_REQUEST)
	except (EmailOTPDevice.DoesNotExist):
		return Response({"error": "OTP WRONG."}, status=status.HTTP_400_BAD_REQUEST)
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