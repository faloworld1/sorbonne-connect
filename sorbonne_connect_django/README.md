# Prototype Django — Chatbot Sorbonne Connect (USPN)

## Description

Ce projet est un **prototype Django** du chatbot Sorbonne Connect, combinant :
- **Base de connaissances** : 30 questions/réponses sur la vie à l'USPN (scolarité, campus, vie étudiante, stages, bourses, numérique)
- **Matching par mots-clés** : algorithme de recherche déterministe côté serveur (Python/Django)
- **Interface de chat** : UI identique au prototype HTML, avec messages, boutons rapides, satisfaction et statistiques
- **Logs** : chaque interaction est enregistrée dans une base SQLite et consultable via le panneau de logs
- **Interface admin** : accès à `/admin/` pour gérer les Q/R et consulter les logs

## Installation rapide

```powershell
# 1. Se placer dans le dossier du projet
cd sorbonne_connect_django

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# 3. Installer Django
pip install -r requirements.txt

# 4. Créer la base de données
python manage.py migrate

# 5. Charger les 30 questions de la base de connaissances
python manage.py load_knowledge_base

# 6. (Optionnel) Créer un superuser pour l'interface admin
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

## Accès

- **Chatbot** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **API envoyer message** : POST http://127.0.0.1:8000/api/send/
- **API satisfaction** : POST http://127.0.0.1:8000/api/satisfaction/
- **API statistiques** : GET http://127.0.0.1:8000/api/stats/
- **API logs** : GET http://127.0.0.1:8000/api/logs/

## Architecture

```
sorbonne_connect_django/
├── manage.py
├── requirements.txt
├── sorbonne_connect/          # Projet Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── chatbot/                   # Application chatbot
    ├── models.py              # BaseConnaissance + LogChatbot
    ├── views.py               # Pages + API JSON
    ├── urls.py                # Routes
    ├── admin.py               # Interface admin
    ├── templates/chatbot/
    │   └── index.html         # Interface du chatbot
    └── management/commands/
        └── load_knowledge_base.py  # Commande pour charger les 30 Q/R
```

## Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| Chat en temps réel | Envoi de messages avec réponse instantanée du serveur Django |
| Matching par mots-clés | Algorithme de scoring : correspondance exacte (×3) + mots individuels (×1) |
| Boutons rapides | 10 raccourcis thématiques (emploi du temps, absence, Wi-Fi, etc.) |
| Satisfaction | Boutons 👍/👎 sur chaque réponse, enregistrés en base |
| Statistiques | Compteurs de messages, matchs, fallbacks et taux de réussite |
| Panneau de logs | Consultation des 50 dernières interactions |
| Interface admin | Gestion complète des Q/R et des logs via /admin/ |

## Équipe

Projet MasterLab BIDABI — Université Sorbonne Paris Nord (USPN)
