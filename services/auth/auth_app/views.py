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
    # Manejar el registro cuando es una petición POST
    print("Entrando en Serializer")
    print("Datos de la petición: ", request.data)
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario registrado correctamente."}, status=status.HTTP_201_CREATED)
    print("Saliendo de Serializer Con Errores: ", serializer.errors) 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    print("ENTRANDO EN -> validate_token_view")
    token = request.COOKIES.get('accessToken')  # Obtener el token de las cookies
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

    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Decodificar el refresh token y generar un nuevo access token
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)

        return Response({
            'access_token': new_access_token,
        }, status=status.HTTP_200_OK)
    except TokenError as e:
        # Manejar errores si el token es inválido o expiró
        return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)