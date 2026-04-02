from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Utilisateur


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur",
            'autofocus': True,
        }),
        label="Nom d'utilisateur",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
        }),
        label='Mot de passe',
    )


class InscriptionForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'numero_etudiant', 'formation', 'telephone',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'numero_etudiant': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = [
            'first_name', 'last_name', 'email',
            'telephone', 'formation', 'numero_etudiant',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_etudiant': forms.TextInput(attrs={'class': 'form-control'}),
        }
