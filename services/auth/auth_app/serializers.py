from rest_framework import serializers
from .models import CustomUser  # Importa tu modelo personalizado

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', "auth_method"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            auth_method=validated_data['auth_method']
        )
        user.is_active = False  # ❗ CREO QUE ESTA DUB¿PLICADO
        user.save()
        return user