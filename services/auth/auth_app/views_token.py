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

@api_view(['GET'])
def validate_token_view(request):
    token = request.COOKIES.get('accessToken')  # Obtener el token de las cookies
    print("validate_token_view, token -> ", str(token))
    if not token:
        print("validate_token_view, not token found")
        return Response({'error': 'accessToken not found in cookies'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print("validate_token_view, OK, 200")
        return Response({'valid': True, 'payload': payload}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        print("validate_token_view, token has expired, 401")
        return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        print("validate_token_view, invalid token, 401")
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET'])
def refresh_token_view(request):
    print("ENTRANDO A refresh_token_view, token -> ")
    refresh_token = request.COOKIES.get('refresh_token')
    print("refresh-token-view ", refresh_token)
    if not refresh_token:
        return Response({'error': 'Refresh token not found'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)

        return Response({
            'access_token': new_access_token,
        }, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({'error': 'Invalid or expired refresh token', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)