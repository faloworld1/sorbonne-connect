from django.db import models


class BaseConnaissance(models.Model):
    """Table des questions/réponses de la base de connaissances."""

    CATEGORIE_CHOICES = [
        ('Scolarité', 'Scolarité'),
        ('Vie étudiante', 'Vie étudiante'),
        ('Campus', 'Campus'),
        ('Stages', 'Stages'),
        ('Bourses', 'Bourses'),
        ('Numérique', 'Numérique'),
    ]

    question = models.TextField(verbose_name="Question")
    reponse = models.TextField(verbose_name="Réponse")
    mots_cles = models.TextField(
        verbose_name="Mots-clés",
        help_text="Mots-clés séparés par des points-virgules (;)"
    )
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    lien_document = models.URLField(blank=True, default="", verbose_name="Lien document")

    class Meta:
        verbose_name = "Question de la base"
        verbose_name_plural = "Base de connaissances"
        ordering = ['id']

    def __str__(self):
        return f"Q{self.id}: {self.question[:80]}"

    def get_mots_cles_list(self):
        return [mc.strip().lower() for mc in self.mots_cles.split(';') if mc.strip()]


class LogChatbot(models.Model):
    """Logs des interactions avec le chatbot."""

    SATISFACTION_CHOICES = [
        ('', 'Non évalué'),
        ('Utile', 'Utile'),
        ('Pas utile', 'Pas utile'),
    ]

    date_heure = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure")
    session_id = models.CharField(max_length=100, verbose_name="Session", default="")
    question_posee = models.TextField(verbose_name="Question posée")
    reponse_fournie = models.TextField(verbose_name="Réponse fournie")
    match_trouve = models.BooleanField(default=False, verbose_name="Match trouvé")
    question_matchee = models.ForeignKey(
        BaseConnaissance, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="Question matchée"
    )
    satisfaction = models.CharField(
        max_length=20, choices=SATISFACTION_CHOICES, blank=True, default="",
        verbose_name="Satisfaction"
    )

    class Meta:
        verbose_name = "Log chatbot"
        verbose_name_plural = "Logs chatbot"
        ordering = ['-date_heure']

    def __str__(self):
        status = "✅" if self.match_trouve else "❌"
        return f"{status} {self.date_heure:%d/%m %H:%M} — {self.question_posee[:60]}"
