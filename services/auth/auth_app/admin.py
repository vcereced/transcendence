from django.contrib import admin
from .models import CustomUser, Friendship

admin.register([
	CustomUser,
	Friendship,
])
