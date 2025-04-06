from django.contrib import admin
from .models import Tournament
# Register your models here.


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'tournament_tree')
    search_fields = ('name',)
    ordering = ('-created_at',)

admin.site.register(Tournament, TournamentAdmin)