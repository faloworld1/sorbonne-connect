from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentification & comptes
    path('', include('accounts.urls')),

    # Chatbot
    path('', include('chatbot.urls')),

    # Campus (événements, publications, associations, cours, émargement)
    path('campus/', include('campus.urls')),

    # Reporting & exports Power BI
    path('reporting/', include('reporting.urls')),
]
