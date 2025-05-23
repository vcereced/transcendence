# Generated by Django 4.1.13 on 2025-04-19 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'blank': 'El nombre de usuario no puede ser solo espacios vacíos---', 'invalid': 'Los nombres de usuario solo pueden contener letras y números---', 'max_length': 'El nombre de usuario es demasiado largo, mantenlo por debajo de 20 caracteres---', 'required': 'Un nombre de usuario es absolutamente necesario---', 'unique': '¡Vaya! Este nombre de usuario ya está en uso. Por favor, elige otro---'}, max_length=20, unique=True, verbose_name='username'),
        ),
    ]
