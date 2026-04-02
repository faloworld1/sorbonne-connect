from django.contrib import admin
from .models import Association, Evenement, Publication, Cours, Emargement, Annonce


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'responsable', 'active', 'date_creation')
    list_filter = ('active',)
    search_fields = ('nom', 'description')


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_debut', 'lieu', 'organisateur', 'statut')
    list_filter = ('statut', 'date_debut')
    search_fields = ('titre', 'description')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'statut', 'date_creation')
    list_filter = ('statut',)
    search_fields = ('titre', 'contenu')


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'enseignant', 'formation', 'jour', 'heure_debut', 'heure_fin', 'salle')
    list_filter = ('jour', 'formation')
    search_fields = ('nom', 'formation')


@admin.register(Emargement)
class EmargementAdmin(admin.ModelAdmin):
    list_display = ('cours', 'etudiant', 'date', 'present')
    list_filter = ('present', 'date', 'cours')
    search_fields = ('etudiant__last_name', 'etudiant__first_name')


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'priorite', 'auteur', 'date_creation', 'active')
    list_filter = ('priorite', 'active')
    search_fields = ('titre', 'contenu')
