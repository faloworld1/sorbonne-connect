from django import template
from django.db.models import Q
from django.utils import timezone

from accounts.models import Utilisateur
from campus.models import Annonce, Evenement, Publication, Association, Cours

register = template.Library()


@register.simple_tag
def get_annonces_for_user(user):
    qs = Annonce.objects.filter(active=True)
    qs = qs.filter(Q(destinataires_role='') | Q(destinataires_role=user.role))
    return qs[:10]


@register.simple_tag
def get_upcoming_events():
    return Evenement.objects.filter(
        statut='approuve', date_debut__gte=timezone.now(),
    )[:10]


@register.simple_tag
def get_pending_events():
    return Evenement.objects.filter(statut='en_attente')[:10]


@register.simple_tag
def get_recent_publications():
    return Publication.objects.filter(statut='publie')[:10]


@register.simple_tag
def get_user_associations(user):
    return Association.objects.filter(responsable=user, active=True)


@register.simple_tag
def get_user_events(user):
    return Evenement.objects.filter(organisateur=user)[:10]


@register.simple_tag
def get_cours_for_enseignant(user):
    return Cours.objects.filter(enseignant=user)


@register.simple_tag
def get_platform_stats():
    return {
        'utilisateurs': Utilisateur.objects.count(),
        'evenements': Evenement.objects.filter(statut='approuve').count(),
        'publications': Publication.objects.filter(statut='publie').count(),
        'associations': Association.objects.filter(active=True).count(),
    }
