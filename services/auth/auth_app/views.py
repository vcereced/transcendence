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
from django.contrib.auth.models import User
from auth_app.utils.utils import genTOPTDevice, activateTOPTDevice, verifyTOPTDevice

SECRET_KEY = os.getenv("JWT_SECRET")

@api_view(['POST'])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False  # Desactivamos la cuenta hasta que confirme el OTP
        user.save()

        qr_base64 = genTOPTDevice(user)

        return Response({
            "message": "User register OK. Scan QR to set 2FA.",
            "qr_code": qr_base64,  # Enviar QR en base64 para mostrar en frontend
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp_view(request):
    username = request.data.get("username")
    otp_token = request.data.get("otp_token")

    if not username or not otp_token:
        return Response({"error": "not found username or otp."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "user not found."}, status=status.HTTP_404_NOT_FOUND)

    if activateTOPTDevice(user, otp_token):
        user.is_active = True  # Activamos la cuenta
        user.save()
        return Response({"message": "OTP OK. User active, go to login."}, status=status.HTTP_200_OK)
    
    return Response({"error": "Código OTP wrong."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api_view(request):

	username = request.data.get('username')
	password = request.data.get('password')
	otp_token = request.data.get('otp_token')

	user = authenticate(username=username, password=password)

	if user is not None and verifyTOPTDevice(user, otp_token) is not None:
        
		refresh = RefreshToken.for_user(user)
		refresh['username'] = user.username

		return Response({
			'message': 'Inicio de sesión exitoso.',
			'refresh': str(refresh),
			'access': str(refresh.access_token)
		}, status=status.HTTP_200_OK)
	else:
		return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_400_BAD_REQUEST)
	
@api_view(['GET'])
def validate_token_view(request):

    token = request.COOKIES.get('accessToken')

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
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)

        return Response({
            'access_token': new_access_token,
        }, status=status.HTTP_200_OK)
    
    except TokenError as e:
        return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)