from django.db import models

# Create your models here.
from django.db import models

class Tournament(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # players = models.ManyToManyField('auth.User')  # Usamos el modelo User por defecto de Django

    def __str__(self):
        return self.name
