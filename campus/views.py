import json
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from .models import (
    Association, Evenement, Publication, Cours, Emargement, Annonce,
)
from .forms import (
    EvenementForm, PublicationForm, AnnonceForm, AssociationForm, CoursForm,
)


# ──────────────────── Événements ────────────────────

@login_required
def liste_evenements(request):
    evenements = Evenement.objects.filter(statut='approuve')
    return render(request, 'campus/evenements.html', {'evenements': evenements})


@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            evt = form.save(commit=False)
            evt.organisateur = request.user
            evt.save()
            messages.success(request, 'Événement créé (en attente de validation).')
            return redirect('campus:evenements')
    else:
        form = EvenementForm()
    return render(request, 'campus/evenement_form.html', {'form': form, 'titre': 'Créer un événement'})


@role_required('admin_univ', 'bde')
def moderer_evenements(request):
    evenements = Evenement.objects.filter(statut='en_attente')
    return render(request, 'campus/moderation_evenements.html', {'evenements': evenements})


@role_required('admin_univ', 'bde')
@require_POST
def valider_evenement(request, pk):
    evt = get_object_or_404(Evenement, pk=pk)
    action = request.POST.get('action')
    if action == 'approuver':
        evt.statut = 'approuve'
        messages.success(request, f'Événement « {evt.titre} » approuvé.')
    elif action == 'refuser':
        evt.statut = 'refuse'
        messages.info(request, f'Événement « {evt.titre} » refusé.')
    evt.save()
    return redirect('campus:moderer_evenements')


# ──────────────────── Publications ────────────────────

@login_required
def liste_publications(request):
    publications = Publication.objects.filter(statut='publie')
    return render(request, 'campus/publications.html', {'publications': publications})


@role_required('bde', 'admin_univ')
def creer_publication(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.auteur = request.user
            pub.save()
            messages.success(request, 'Publication créée.')
            return redirect('campus:publications')
    else:
        form = PublicationForm()
    return render(request, 'campus/publication_form.html', {'form': form, 'titre': 'Nouvelle publication'})


@role_required('bde', 'admin_univ')
def modifier_publication(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=pub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication mise à jour.')
            return redirect('campus:publications')
    else:
        form = PublicationForm(instance=pub)
    return render(request, 'campus/publication_form.html', {'form': form, 'titre': 'Modifier la publication'})


# ──────────────────── Annonces ────────────────────

@login_required
def liste_annonces(request):
    annonces = Annonce.objects.filter(active=True)
    user_role = request.user.role
    annonces = annonces.filter(
        Q(destinataires_role='') | Q(destinataires_role=user_role)
    )
    return render(request, 'campus/annonces.html', {'annonces': annonces})


@role_required('admin_univ')
def creer_annonce(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.auteur = request.user
            ann.save()
            messages.success(request, 'Annonce publiée.')
            return redirect('campus:annonces')
    else:
        form = AnnonceForm()
    return render(request, 'campus/annonce_form.html', {'form': form, 'titre': 'Nouvelle annonce'})


# ──────────────────── Associations ────────────────────

@login_required
def liste_associations(request):
    associations = Association.objects.filter(active=True)
    return render(request, 'campus/associations.html', {'associations': associations})


@role_required('association', 'admin_univ')
def creer_association(request):
    if request.method == 'POST':
        form = AssociationForm(request.POST)
        if form.is_valid():
            asso = form.save(commit=False)
            asso.responsable = request.user
            asso.save()
            messages.success(request, 'Association créée.')
            return redirect('campus:associations')
    else:
        form = AssociationForm()
    return render(request, 'campus/association_form.html', {'form': form, 'titre': 'Créer une association'})


@login_required
@require_POST
def rejoindre_association(request, pk):
    asso = get_object_or_404(Association, pk=pk, active=True)
    asso.membres.add(request.user)
    messages.success(request, f'Vous avez rejoint « {asso.nom} ».')
    return redirect('campus:associations')


# ──────────────────── Cours & Emploi du temps ────────────────────

@login_required
def emploi_du_temps(request):
    user = request.user
    if user.role == 'enseignant':
        cours = Cours.objects.filter(enseignant=user)
    elif user.role == 'etudiant' and user.formation:
        cours = Cours.objects.filter(formation=user.formation)
    else:
        cours = Cours.objects.none()
    return render(request, 'campus/emploi_du_temps.html', {'cours': cours})


@role_required('enseignant', 'admin_univ')
def creer_cours(request):
    if request.method == 'POST':
        form = CoursForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.enseignant = request.user
            c.save()
            messages.success(request, 'Cours créé.')
            return redirect('campus:emploi_du_temps')
    else:
        form = CoursForm()
    return render(request, 'campus/cours_form.html', {'form': form, 'titre': 'Ajouter un cours'})


# ──────────────────── Émargement ────────────────────

@role_required('enseignant')
def emargement(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    today = date.today()

    from accounts.models import Utilisateur
    etudiants = Utilisateur.objects.filter(
        role='etudiant', formation=cours.formation,
    ).order_by('last_name', 'first_name')

    if request.method == 'POST':
        presents_ids = request.POST.getlist('presents')
        for etu in etudiants:
            Emargement.objects.update_or_create(
                cours=cours,
                etudiant=etu,
                date=today,
                defaults={'present': str(etu.pk) in presents_ids},
            )
        messages.success(request, 'Émargement enregistré.')
        return redirect('campus:emploi_du_temps')

    emargements_existants = {
        e.etudiant_id: e.present
        for e in Emargement.objects.filter(cours=cours, date=today)
    }

    etudiants_data = []
    for etu in etudiants:
        etudiants_data.append({
            'etudiant': etu,
            'present': emargements_existants.get(etu.pk, False),
        })

    return render(request, 'campus/emargement.html', {
        'cours': cours,
        'etudiants_data': etudiants_data,
        'date': today,
    })
