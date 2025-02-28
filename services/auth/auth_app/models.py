from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django_otp.models import Device

class CustomUser(AbstractUser):  # ⬅️ Ahora es un modelo personalizado
    AUTH_CHOICES = [
        ("None", "None"),
        ("Qr", "Qr"),
        ("Sms", "Sms"),
        ("Email", "Email"),
    ]
    auth_method = models.CharField(max_length=10, choices=AUTH_CHOICES, default="None")

class EmailOTPDevice(Device):
    otp_token = models.CharField(max_length=6, blank=True, null=True)
    valid_until = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp_token = str(random.randint(100000, 999999))  # Código de 6 dígitos
        self.valid_until = now() + timedelta(minutes=5)  # Expira en 5 minutos
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