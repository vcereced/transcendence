from celery import shared_task, current_app
from .models import Box
from .serializers import UserSerializer
from django.db import transaction

# @shared_task(name='process_user_created_event')
# def process_user_created_event(user_data):
#     # Process the user created event
#     serializer = UserSerializer(data=user_data)
#     if not serializer.is_valid():
#         # Log the error and raise an exception
#         raise ValueError(f"Invalid user data: {serializer.errors}")
#     validated_user_data = serializer.validated_data

#     boxes = Box.objects.all()
#     total_units_in_tournament = sum([box.units for box in boxes])
#     if validated_user_data.get('units') > total_units_in_tournament:
#         validated_user_data['status'] = 'DENIED'
#     else:
#         validated_user_data['status'] = 'ACCEPTED'

#     # Emit user processed event
#     transaction.on_commit(lambda: current_app.send_task(
#         'receive_user_processed_event', 
#         args=[validated_user_data], 
#         queue='tournament_events'
#     ))
