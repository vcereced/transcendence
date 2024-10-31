from celery import shared_task
# from .models import User
# from .serializers import UserSerializer

# @shared_task(name='receive_user_processed_event')
# def receive_user_processed_event(processed_user_data):
#     user_id = processed_user_data.get('id')
#     if not user_id:
#         # Log the error and raise an exception
#         raise ValueError("User ID is required to update an user.")

#     try:
#         user = User.objects.get(pk=user_id)
#     except User.DoesNotExist:
#         # Log the error and raise an exception
#         raise ValueError(f"User with ID {user_id} does not exist.")

#     serializer = UserSerializer(user, data=processed_user_data)
#     if not serializer.is_valid():
#         # Log the error and raise an exception
#         raise ValueError(f"Invalid user data: {serializer.errors}")

#     serializer.save()
