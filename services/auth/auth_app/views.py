from django.shortcuts import render
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import RegisterSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import jwt
import os
import qrcode
import base64
from io import BytesIO
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.models import User

SECRET_KEY = os.getenv("JWT_SECRET")
# Create your views here.

def base_view(request):
	contexto_ = {
		'titulo': 'Página de Inicio',
		'descripcion': 'Bienvenido a la página de inicio de nuestro sitio web.'
	}
    # print('request_', request)
	
	if request.method == 'POST':
		# Leer el cuerpo de la solicitud
		body_unicode = request.body.decode('utf-8')
		body_data = json.loads(body_unicode)  # Convertir el JSON en un diccionario

		print('body_data', body_data)
	return render(request, 'base.html', contexto_)  # Renderiza la plantilla index.html

@api_view(['POST'])
def register_view(request):
    print("Entrando en Serializer")
    print("Datos de la petición: ", request.data)
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False  # Desactivamos la cuenta hasta que confirme el OTP
        user.save()

        # Crear un dispositivo TOTP para el usuario
        totp_device = TOTPDevice.objects.create(user=user, confirmed=False)

        # Generar URL para Google Authenticator
        otp_url = totp_device.config_url

        # Generar QR code
        qr = qrcode.make(otp_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            "message": "Usuario registrado correctamente. Escanea el QR para configurar 2FA.",
            "qr_code": qr_base64,  # Enviar QR en base64 para mostrar en frontend
            "otp_url": otp_url  # O enviar la URL para que el frontend genere el QR 
        }, status=status.HTTP_201_CREATED)

    print("Saliendo de Serializer Con Errores: ", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp_view(request):
    username = request.data.get("username")
    otp_token = request.data.get("otp_token")

    if not username or not otp_token:
        return Response({"error": "Faltan datos (username y otp_token)."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Buscar el dispositivo TOTP del usuario
    try:
        totp_device = TOTPDevice.objects.get(user=user, confirmed=False)
    except TOTPDevice.DoesNotExist:
        return Response({"error": "No hay configuración de 2FA pendiente."}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar OTP
    if totp_device.verify_token(otp_token):
        totp_device.confirmed = True  # Confirmamos que el dispositivo es válido
        totp_device.save()
        
        user.is_active = True  # Activamos la cuenta
        user.save()

        return Response({"message": "OTP válido. Usuario activado correctamente.Puedes iniciar sesión ahora."}, status=status.HTTP_200_OK)
    
    return Response({"error": "Código OTP incorrecto."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api_view(request):
	print("Entrando en login_api_view")
	print("Datos de la petición: ", request.data)
	username = request.data.get('username')
	password = request.data.get('password')

	user = authenticate(username=username, password=password)
	if user is not None:
		refresh = RefreshToken.for_user(user)
		refresh['username'] = user.username

		print("TOKEN access: ", str(refresh.access_token))

		return Response({
			'success': True,
			'message': 'Inicio de sesión exitoso en django.',
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}, status=status.HTTP_200_OK)
	else:
		return Response({'message': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(['GET'])
def validate_token_view(request):

    token = request.COOKIES.get('accessToken')
    print("validate_token_view: ", str(token))

    if not token:
        return Response({'error': 'accessToken is required in cookies'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return Response({'valid': True, 'payload': payload}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def refresh_token_view(request):

    refresh_token = request.data.get('refresh_token')
    print("refresh_token ->: ", str(refresh_token))

    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)

        print("new_token ->: ", str(new_access_token))

        return Response({
            'access_token': new_access_token,
        }, status=status.HTTP_200_OK)
    
    except TokenError as e:
        return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)