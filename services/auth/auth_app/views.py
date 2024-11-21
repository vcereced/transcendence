from django.shortcuts import render
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import RegisterSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
		return Response({
			'success': True,
			'message': 'Inicio de sesión exitoso en django.',
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}, status=status.HTTP_200_OK)
	else:
		return Response({'message': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)