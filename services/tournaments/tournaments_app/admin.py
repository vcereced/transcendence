from django.contrib import admin
from .models import Tournament, Participant

from django.utils.safestring import mark_safe
import json

# Register your models here.


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'champion', 'tournament_tree')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username')
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(Tournament, TournamentAdmin)