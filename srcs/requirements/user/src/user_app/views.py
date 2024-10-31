from .models import User
from .serializers import UserSerializer
from celery import current_app
from django.http import Http404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics



# class UserList(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def perform_create(self, serializer):
#         created_user = serializer.save()
#         created_user_data = UserSerializer(created_user).data
#         print(f"Created user: {created_user_data}")
#         # emit user created event
#         transaction.on_commit(lambda: current_app.send_task(
#             'process_user_created_event', 
#             args=[created_user_data], 
#             queue='user_events',
#         ))



# class UserDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
