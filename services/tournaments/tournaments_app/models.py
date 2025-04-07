
# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Tournament(models.Model):

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tournament_tree = models.JSONField(default=dict) 
    # champion = models.CharField(max_length=100, blank=True, null=True) #user foreign key
    champion = models.ForeignKey('Participant', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_tournaments')
    participants = models.ManyToManyField('Participant', blank=True)

    def __str__(self):
        return self.name

class Participant(models.Model):

    user_id = models.IntegerField(unique=False)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username
