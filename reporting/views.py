import csv
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.decorators import role_required
from accounts.models import Utilisateur
from campus.models import Evenement, Publication, Emargement, Cours, Annonce, Association
from chatbot.models import LogChatbot, BaseConnaissance


def powerbi_api_key_required(view_func):
    """Vérifie la clé API passée en paramètre ?api_key= ou en header Authorization."""
    @wraps(view_func)
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
        api_key = request.GET.get('api_key') or request.headers.get('X-API-Key', '')
        if not api_key or api_key != settings.POWERBI_API_KEY:
            return JsonResponse(
                {'error': 'Clé API invalide. Passez ?api_key=VOTRE_CLE ou le header X-API-Key.'},
                status=403,
            )
        return view_func(request, *args, **kwargs)
    return wrapper


# ──────────────────── Dashboard interne ────────────────────

@role_required('admin_univ')
def dashboard_reporting(request):
    """Tableau de bord analytique interne."""
    now = timezone.now()
    trente_jours = now - timedelta(days=30)

    context = {
        # Utilisateurs
        'total_utilisateurs': Utilisateur.objects.count(),
        'utilisateurs_par_role': list(
            Utilisateur.objects.values('role').annotate(total=Count('id')).order_by('role')
        ),
        # Chatbot
        'total_interactions': LogChatbot.objects.count(),
        'interactions_30j': LogChatbot.objects.filter(date_heure__gte=trente_jours).count(),
        'taux_match': _taux_match(),
        'satisfaction_stats': _satisfaction_stats(),
        # Campus
        'total_evenements': Evenement.objects.count(),
        'evenements_approuves': Evenement.objects.filter(statut='approuve').count(),
        'total_publications': Publication.objects.filter(statut='publie').count(),
        'total_associations': Association.objects.filter(active=True).count(),
        'total_annonces': Annonce.objects.filter(active=True).count(),
        # Assiduité
        'taux_assiduite': _taux_assiduite(),
    }
    return render(request, 'reporting/dashboard.html', context)


def _taux_match():
    total = LogChatbot.objects.count()
    if total == 0:
        return 0
    matchs = LogChatbot.objects.filter(match_trouve=True).count()
    return round(matchs / total * 100, 1)


def _satisfaction_stats():
    total_evalue = LogChatbot.objects.exclude(satisfaction='').count()
    if total_evalue == 0:
        return {'utile': 0, 'pas_utile': 0, 'total': 0}
    utile = LogChatbot.objects.filter(satisfaction='Utile').count()
    pas_utile = LogChatbot.objects.filter(satisfaction='Pas utile').count()
    return {'utile': utile, 'pas_utile': pas_utile, 'total': total_evalue}


def _taux_assiduite():
    total = Emargement.objects.count()
    if total == 0:
        return 0
    presents = Emargement.objects.filter(present=True).count()
    return round(presents / total * 100, 1)


# ──────────────────── Exports CSV pour Power BI ────────────────────

@role_required('admin_univ')
def export_chatbot_logs(request):
    """Export CSV des logs chatbot pour Power BI."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="chatbot_logs.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Date', 'Heure', 'Session', 'Question posée',
        'Réponse fournie', 'Match trouvé', 'Catégorie matchée', 'Satisfaction',
    ])

    for log in LogChatbot.objects.select_related('question_matchee').iterator():
        writer.writerow([
            log.id,
            log.date_heure.strftime('%Y-%m-%d'),
            log.date_heure.strftime('%H:%M:%S'),
            log.session_id,
            log.question_posee,
            log.reponse_fournie[:200],
            'Oui' if log.match_trouve else 'Non',
            log.question_matchee.categorie if log.question_matchee else '',
            log.satisfaction or 'Non évalué',
        ])

    return response


@role_required('admin_univ')
def export_emargements(request):
    """Export CSV des émargements pour Power BI."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="emargements.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Date', 'Cours', 'Formation', 'Enseignant',
        'Étudiant', 'Numéro étudiant', 'Présent',
    ])

    for e in Emargement.objects.select_related('cours', 'cours__enseignant', 'etudiant').iterator():
        writer.writerow([
            e.id,
            e.date.strftime('%Y-%m-%d'),
            e.cours.nom,
            e.cours.formation,
            e.cours.enseignant.get_full_name(),
            e.etudiant.get_full_name(),
            e.etudiant.numero_etudiant,
            'Oui' if e.present else 'Non',
        ])

    return response


@role_required('admin_univ')
def export_evenements(request):
    """Export CSV des événements pour Power BI."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="evenements.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Titre', 'Date début', 'Date fin', 'Lieu',
        'Organisateur', 'Association', 'Statut', 'Date création',
    ])

    for evt in Evenement.objects.select_related('organisateur', 'association').iterator():
        writer.writerow([
            evt.id,
            evt.titre,
            evt.date_debut.strftime('%Y-%m-%d %H:%M'),
            evt.date_fin.strftime('%Y-%m-%d %H:%M'),
            evt.lieu,
            evt.organisateur.get_full_name(),
            evt.association.nom if evt.association else '',
            evt.get_statut_display(),
            evt.date_creation.strftime('%Y-%m-%d'),
        ])

    return response


@role_required('admin_univ')
def export_utilisateurs(request):
    """Export CSV des utilisateurs pour Power BI."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="utilisateurs.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Username', 'Nom', 'Prénom', 'Email',
        'Rôle', 'Formation', 'Numéro étudiant', 'Date inscription', 'Actif',
    ])

    for u in Utilisateur.objects.iterator():
        writer.writerow([
            u.id,
            u.username,
            u.last_name,
            u.first_name,
            u.email,
            u.get_role_display(),
            u.formation,
            u.numero_etudiant,
            u.date_joined.strftime('%Y-%m-%d'),
            'Oui' if u.is_active else 'Non',
        ])

    return response


# ──────────────────── API JSON (alternative Power BI) ────────────────────

@role_required('admin_univ')
def api_stats_globales(request):
    """API JSON statistiques globales pour Power BI / dashboards."""
    now = timezone.now()
    trente_jours = now - timedelta(days=30)

    data = {
        'utilisateurs': {
            'total': Utilisateur.objects.count(),
            'par_role': list(
                Utilisateur.objects.values('role').annotate(count=Count('id'))
            ),
        },
        'chatbot': {
            'total_interactions': LogChatbot.objects.count(),
            'interactions_30j': LogChatbot.objects.filter(date_heure__gte=trente_jours).count(),
            'taux_match': _taux_match(),
            'satisfaction': _satisfaction_stats(),
        },
        'campus': {
            'evenements_total': Evenement.objects.count(),
            'evenements_approuves': Evenement.objects.filter(statut='approuve').count(),
            'publications': Publication.objects.filter(statut='publie').count(),
            'associations': Association.objects.filter(active=True).count(),
        },
        'assiduite': {
            'taux_global': _taux_assiduite(),
            'total_emargements': Emargement.objects.count(),
        },
    }
    return JsonResponse(data)


# ══════════════════════════════════════════════════════════════
# API Power BI — accessibles par clé API (sans session Django)
# Usage: http://127.0.0.1:8000/reporting/powerbi/...?api_key=VOTRE_CLE
# ══════════════════════════════════════════════════════════════

@powerbi_api_key_required
def powerbi_stats(request):
    """JSON — Statistiques globales pour Power BI."""
    now = timezone.now()
    trente_jours = now - timedelta(days=30)

    data = {
        'utilisateurs': {
            'total': Utilisateur.objects.count(),
            'par_role': list(
                Utilisateur.objects.values('role').annotate(count=Count('id'))
            ),
        },
        'chatbot': {
            'total_interactions': LogChatbot.objects.count(),
            'interactions_30j': LogChatbot.objects.filter(date_heure__gte=trente_jours).count(),
            'taux_match': _taux_match(),
            'satisfaction': _satisfaction_stats(),
        },
        'campus': {
            'evenements_total': Evenement.objects.count(),
            'evenements_approuves': Evenement.objects.filter(statut='approuve').count(),
            'publications': Publication.objects.filter(statut='publie').count(),
            'associations': Association.objects.filter(active=True).count(),
        },
        'assiduite': {
            'taux_global': _taux_assiduite(),
            'total_emargements': Emargement.objects.count(),
        },
    }
    return JsonResponse(data)


@powerbi_api_key_required
def powerbi_chatbot_logs(request):
    """JSON — Tous les logs chatbot (format tableau pour Power BI)."""
    logs = []
    for log in LogChatbot.objects.select_related('question_matchee').iterator():
        logs.append({
            'id': log.id,
            'date': log.date_heure.strftime('%Y-%m-%d'),
            'heure': log.date_heure.strftime('%H:%M:%S'),
            'session_id': log.session_id,
            'question_posee': log.question_posee,
            'reponse_fournie': log.reponse_fournie[:200],
            'match_trouve': log.match_trouve,
            'categorie': log.question_matchee.categorie if log.question_matchee else '',
            'satisfaction': log.satisfaction or 'Non évalué',
        })
    return JsonResponse(logs, safe=False)


@powerbi_api_key_required
def powerbi_emargements(request):
    """JSON — Tous les émargements (format tableau pour Power BI)."""
    data = []
    for e in Emargement.objects.select_related('cours', 'cours__enseignant', 'etudiant').iterator():
        data.append({
            'id': e.id,
            'date': e.date.strftime('%Y-%m-%d'),
            'cours': e.cours.nom,
            'formation': e.cours.formation,
            'enseignant': e.cours.enseignant.get_full_name(),
            'etudiant': e.etudiant.get_full_name(),
            'numero_etudiant': e.etudiant.numero_etudiant,
            'present': e.present,
        })
    return JsonResponse(data, safe=False)


@powerbi_api_key_required
def powerbi_evenements(request):
    """JSON — Tous les événements (format tableau pour Power BI)."""
    data = []
    for evt in Evenement.objects.select_related('organisateur', 'association').iterator():
        data.append({
            'id': evt.id,
            'titre': evt.titre,
            'date_debut': evt.date_debut.strftime('%Y-%m-%d %H:%M'),
            'date_fin': evt.date_fin.strftime('%Y-%m-%d %H:%M'),
            'lieu': evt.lieu,
            'organisateur': evt.organisateur.get_full_name(),
            'association': evt.association.nom if evt.association else '',
            'statut': evt.get_statut_display(),
            'date_creation': evt.date_creation.strftime('%Y-%m-%d'),
        })
    return JsonResponse(data, safe=False)


@powerbi_api_key_required
def powerbi_utilisateurs(request):
    """JSON — Tous les utilisateurs (format tableau pour Power BI)."""
    data = []
    for u in Utilisateur.objects.iterator():
        data.append({
            'id': u.id,
            'username': u.username,
            'nom': u.last_name,
            'prenom': u.first_name,
            'email': u.email,
            'role': u.get_role_display(),
            'formation': u.formation,
            'numero_etudiant': u.numero_etudiant,
            'date_inscription': u.date_joined.strftime('%Y-%m-%d'),
            'actif': u.is_active,
        })
    return JsonResponse(data, safe=False)
