from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'numero_etudiant')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Campus', {
            'fields': ('role', 'numero_etudiant', 'formation', 'telephone'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Campus', {
            'fields': ('role', 'first_name', 'last_name', 'email', 'formation'),
        }),
    )
