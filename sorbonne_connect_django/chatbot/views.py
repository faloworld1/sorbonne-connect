import json
import unicodedata
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import BaseConnaissance, LogChatbot


FALLBACK_MESSAGE = (
    "Je suis désolé, je ne peux répondre qu'aux questions concernant la vie à l'USPN "
    "(scolarité, campus, vie étudiante, stages, bourses). Reformulez votre question ou "
    "contactez le secrétariat de votre formation pour une assistance personnalisée."
)


def normalize(text):
    """Supprime les accents, met en minuscules et ne garde que lettres/chiffres/espaces."""
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.strip()


def find_match(user_input):
    """Cherche la meilleure correspondance par mots-clés dans la base."""
    normalized_input = normalize(user_input)
    input_words = normalized_input.split()

    best_match = None
    best_score = 0

    for entry in BaseConnaissance.objects.all():
        score = 0
        for mot_cle in entry.get_mots_cles_list():
            normalized_mc = normalize(mot_cle)
            if normalized_mc in normalized_input:
                score += 3
            else:
                mc_words = normalized_mc.split()
                for mc_word in mc_words:
                    if mc_word in input_words:
                        score += 1

        if score > best_score:
            best_score = score
            best_match = entry

    return best_match if best_score >= 1 else None


@ensure_csrf_cookie
def index(request):
    """Page d'accueil du chatbot."""
    return render(request, 'chatbot/index.html')


@ensure_csrf_cookie
def portal(request):
    """Page d'accueil du portail Campus Connect."""
    return render(request, 'chatbot/portal.html')


@require_POST
def api_send_message(request):
    """API pour envoyer un message au chatbot et recevoir une réponse."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    question = data.get('message', '').strip()
    if not question:
        return JsonResponse({'error': 'Message vide'}, status=400)

    session_id = request.session.session_key or ''
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    match = find_match(question)

    if match:
        response_data = {
            'reponse': match.reponse,
            'match': True,
            'categorie': match.categorie,
            'lien': match.lien_document,
            'question_ref': match.question,
        }
        LogChatbot.objects.create(
            session_id=session_id,
            question_posee=question,
            reponse_fournie=match.reponse,
            match_trouve=True,
            question_matchee=match,
        )
    else:
        response_data = {
            'reponse': FALLBACK_MESSAGE,
            'match': False,
            'categorie': '',
            'lien': '',
            'question_ref': '',
        }
        LogChatbot.objects.create(
            session_id=session_id,
            question_posee=question,
            reponse_fournie=FALLBACK_MESSAGE,
            match_trouve=False,
        )

    return JsonResponse(response_data)


@require_POST
def api_satisfaction(request):
    """API pour enregistrer la satisfaction sur le dernier message."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    log_id = data.get('log_id')
    useful = data.get('useful')

    if log_id is None:
        return JsonResponse({'error': 'log_id manquant'}, status=400)

    try:
        log = LogChatbot.objects.get(id=log_id)
    except LogChatbot.DoesNotExist:
        return JsonResponse({'error': 'Log introuvable'}, status=404)

    log.satisfaction = 'Utile' if useful else 'Pas utile'
    log.save(update_fields=['satisfaction'])

    return JsonResponse({'status': 'ok'})


def api_stats(request):
    """API pour récupérer les statistiques du chatbot."""
    total = LogChatbot.objects.count()
    matchs = LogChatbot.objects.filter(match_trouve=True).count()
    fallbacks = total - matchs

    return JsonResponse({
        'total': total,
        'match': matchs,
        'fallback': fallbacks,
        'rate': round(matchs / total * 100) if total > 0 else 0,
    })


def api_logs(request):
    """API pour récupérer les derniers logs."""
    logs = LogChatbot.objects.all()[:50]
    data = []
    for log in logs:
        data.append({
            'id': log.id,
            'date': log.date_heure.strftime('%d/%m/%Y %H:%M'),
            'question': log.question_posee,
            'match': log.match_trouve,
            'question_ref': log.question_matchee.question if log.question_matchee else '',
            'satisfaction': log.satisfaction,
        })
    return JsonResponse({'logs': data})
