from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé avec gestion des rôles."""

    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('bde', 'BDE'),
        ('association', 'Association'),
        ('admin_univ', 'Administrateur Université'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='etudiant',
        verbose_name='Rôle',
    )
    numero_etudiant = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Numéro étudiant',
    )
    formation = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Formation',
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Téléphone',
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_etudiant(self):
        return self.role == 'etudiant'

    @property
    def is_enseignant(self):
        return self.role == 'enseignant'

    @property
    def is_bde(self):
        return self.role == 'bde'

    @property
    def is_association(self):
        return self.role == 'association'

    @property
    def is_admin_univ(self):
        return self.role == 'admin_univ'
