from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    # Dashboard interne
    path('', views.dashboard_reporting, name='dashboard'),

    # Exports CSV pour Power BI (nécessite session admin)
    path('export/chatbot/', views.export_chatbot_logs, name='export_chatbot'),
    path('export/emargements/', views.export_emargements, name='export_emargements'),
    path('export/evenements/', views.export_evenements, name='export_evenements'),
    path('export/utilisateurs/', views.export_utilisateurs, name='export_utilisateurs'),

    # API JSON (nécessite session admin)
    path('api/stats/', views.api_stats_globales, name='api_stats'),

    # API Power BI — accessibles par clé API (sans session Django)
    # Usage: /reporting/powerbi/...?api_key=campus-connect-powerbi-2026
    path('powerbi/stats/', views.powerbi_stats, name='powerbi_stats'),
    path('powerbi/chatbot/', views.powerbi_chatbot_logs, name='powerbi_chatbot'),
    path('powerbi/emargements/', views.powerbi_emargements, name='powerbi_emargements'),
    path('powerbi/evenements/', views.powerbi_evenements, name='powerbi_evenements'),
    path('powerbi/utilisateurs/', views.powerbi_utilisateurs, name='powerbi_utilisateurs'),
]
