from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django_otp.models import Device
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):  
    
    email = models.EmailField(unique=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True, default="/media/default.gif")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
  

class EmailOTPDevice(Device):
    otp_token = models.CharField(max_length=6, blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)

    def generate_otp(self):
        self.otp_token = str(random.randint(100000, 999999))  # Código de 6 dígitos
        self.valid_until = now() + timedelta(minutes=1)  # Expira en 5 minutos
        self.email = self.user.email
        self.save()

    def send_otp(self):
        print("ENVIANDO al email: ", self.user.email, "el token: ", self.otp_token)

        send_mail(
            'OTP sended by PONG',
            f'Tu código de autenticación es: {self.otp_token} ',
            'victorcerecedagonzalez@gmail.com',
            [self.user.email],
            fail_silently=False,
        )

class Friendship(models.Model):
    user1 = models.CharField(max_length=150)  # Guardará el username en lugar del ID
    user2 = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship')
        ]

    def __str__(self):
        return f"{self.user1} is friends with {self.user2}"

    @staticmethod
    def are_friends(username_a: str, username_b: str):
        """Verifica si dos usuarios son amigos"""
        user_a, user_b = sorted([username_a, username_b])  # Orden alfabético
        return Friendship.objects.filter(user1=user_a, user2=user_b).exists()

    @staticmethod
    def add_friend(username_a: str, username_b: str):
        """Añade una amistad entre dos usuarios si no existe ya"""
        if username_a == username_b:
            return False  # No puedes ser amigo de ti mismo

        user_a, user_b = sorted([username_a, username_b])  # Ordena alfabéticamente

        if not Friendship.are_friends(user_a, user_b):
            Friendship.objects.create(user1=user_a, user2=user_b)
            return True
        return False

    @staticmethod
    def remove_friend(username_a: str, username_b: str):
        """Elimina una amistad si existe"""
        user_a, user_b = sorted([username_a, username_b])  # Ordena alfabéticamente

        friendship = Friendship.objects.filter(user1=user_a, user2=user_b).first()
        if friendship:
            friendship.delete()
            return True
        return False