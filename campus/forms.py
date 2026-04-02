from django import forms
from .models import Evenement, Publication, Annonce, Association, Cours


class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['titre', 'description', 'date_debut', 'date_fin', 'lieu', 'association']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date_debut': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'date_fin': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'association': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_debut'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_fin'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['association'].required = False


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['titre', 'contenu', 'statut']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['titre', 'contenu', 'priorite', 'destinataires_role']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'destinataires_role': forms.Select(
                attrs={'class': 'form-control'},
                choices=[('', 'Tous')] + [
                    ('etudiant', 'Étudiants'),
                    ('enseignant', 'Enseignants'),
                    ('bde', 'BDE'),
                    ('association', 'Associations'),
                ],
            ),
        }


class AssociationForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['nom', 'formation', 'jour', 'heure_debut', 'heure_fin', 'salle']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.TextInput(attrs={'class': 'form-control'}),
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'salle': forms.TextInput(attrs={'class': 'form-control'}),
        }
