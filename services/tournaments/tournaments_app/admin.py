from django.contrib import admin
from .models import Tournament, Participant, TournamentParticipant

class TournamentParticipantInline(admin.TabularInline):
    model = TournamentParticipant
    extra = 1  # Número de formularios vacíos que se muestran

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'name', 'created_at', 'champion', 'tournament_tree')
    search_fields = ('name',)
    ordering = ('-created_at',)
    inlines = [TournamentParticipantInline]  # Añade los participantes como inline en el torneo

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username')
    search_fields = ('username',)
    ordering = ('username',)
    inlines = [TournamentParticipantInline]  # Añade los torneos como inline en el participante

admin.site.register(Tournament, TournamentAdmin)
