from django.conf import settings
from django.db import models


class Association(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom')
    description = models.TextField(verbose_name='Description')
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='associations_gerees',
        verbose_name='Responsable',
    )
    membres = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='associations_membre',
        verbose_name='Membres',
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Evenement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    date_debut = models.DateTimeField(verbose_name='Date de début')
    date_fin = models.DateTimeField(verbose_name='Date de fin')
    lieu = models.CharField(max_length=200, verbose_name='Lieu')
    organisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evenements_organises',
        verbose_name='Organisateur',
    )
    association = models.ForeignKey(
        Association,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Association',
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name='Statut',
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.titre} ({self.date_debut:%d/%m/%Y})"


class Publication(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre')
    contenu = models.TextField(verbose_name='Contenu')
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='publications',
        verbose_name='Auteur',
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon',
        verbose_name='Statut',
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre


class Cours(models.Model):
    JOUR_CHOICES = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
    ]

    nom = models.CharField(max_length=200, verbose_name='Nom du cours')
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cours_enseignes',
        verbose_name='Enseignant',
    )
    formation = models.CharField(max_length=100, verbose_name='Formation')
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES, verbose_name='Jour')
    heure_debut = models.TimeField(verbose_name='Heure de début')
    heure_fin = models.TimeField(verbose_name='Heure de fin')
    salle = models.CharField(max_length=50, verbose_name='Salle')

    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['jour', 'heure_debut']

    def __str__(self):
        return f"{self.nom} — {self.get_jour_display()} {self.heure_debut:%H:%M}-{self.heure_fin:%H:%M}"


class Emargement(models.Model):
    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name='emargements',
        verbose_name='Cours',
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emargements',
        verbose_name='Étudiant',
    )
    date = models.DateField(verbose_name='Date')
    present = models.BooleanField(default=False, verbose_name='Présent')
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Émargement'
        verbose_name_plural = 'Émargements'
        unique_together = ['cours', 'etudiant', 'date']
        ordering = ['-date']

    def __str__(self):
        status = '✅' if self.present else '❌'
        return f"{status} {self.etudiant} — {self.cours.nom} ({self.date:%d/%m/%Y})"


class Annonce(models.Model):
    PRIORITE_CHOICES = [
        ('info', 'Information'),
        ('important', 'Important'),
        ('urgent', 'Urgent'),
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre')
    contenu = models.TextField(verbose_name='Contenu')
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annonces',
        verbose_name='Auteur',
    )
    priorite = models.CharField(
        max_length=20,
        choices=PRIORITE_CHOICES,
        default='info',
        verbose_name='Priorité',
    )
    destinataires_role = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Rôle destinataire',
        help_text='Laisser vide pour tous',
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'
        ordering = ['-date_creation']

    def __str__(self):
        return f"[{self.get_priorite_display()}] {self.titre}"
