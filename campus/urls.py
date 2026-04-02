from django.urls import path
from . import views

app_name = 'campus'

urlpatterns = [
    # Événements
    path('evenements/', views.liste_evenements, name='evenements'),
    path('evenements/creer/', views.creer_evenement, name='creer_evenement'),
    path('evenements/moderer/', views.moderer_evenements, name='moderer_evenements'),
    path('evenements/<int:pk>/valider/', views.valider_evenement, name='valider_evenement'),

    # Publications
    path('publications/', views.liste_publications, name='publications'),
    path('publications/creer/', views.creer_publication, name='creer_publication'),
    path('publications/<int:pk>/modifier/', views.modifier_publication, name='modifier_publication'),

    # Annonces
    path('annonces/', views.liste_annonces, name='annonces'),
    path('annonces/creer/', views.creer_annonce, name='creer_annonce'),

    # Associations
    path('associations/', views.liste_associations, name='associations'),
    path('associations/creer/', views.creer_association, name='creer_association'),
    path('associations/<int:pk>/rejoindre/', views.rejoindre_association, name='rejoindre_association'),

    # Emploi du temps & Cours
    path('emploi-du-temps/', views.emploi_du_temps, name='emploi_du_temps'),
    path('cours/creer/', views.creer_cours, name='creer_cours'),

    # Émargement
    path('emargement/<int:cours_id>/', views.emargement, name='emargement'),
]
