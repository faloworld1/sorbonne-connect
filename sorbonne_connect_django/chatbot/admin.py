from django.contrib import admin
from .models import BaseConnaissance, LogChatbot


@admin.register(BaseConnaissance)
class BaseConnaissanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'categorie', 'mots_cles')
    list_filter = ('categorie',)
    search_fields = ('question', 'reponse', 'mots_cles')


@admin.register(LogChatbot)
class LogChatbotAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_heure', 'question_posee', 'match_trouve', 'satisfaction')
    list_filter = ('match_trouve', 'satisfaction')
    search_fields = ('question_posee', 'reponse_fournie')
    readonly_fields = ('date_heure',)
