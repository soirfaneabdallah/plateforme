from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Utilisateur  # Importer votre modèle personnalisé

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre mot de passe',
                'autocomplete': 'new-password',
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirmez votre mot de passe',
                'autocomplete': 'new-password',
            }
        ),
    )
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email','password1','password2'] 
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control','placeholder':'Entrez votre nom'} ),
            'prenom': forms.TextInput(attrs={'class': 'form-control','placeholder':'Entrez votre prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control','placehodelr': 'Entrez votre email'}),
            #'password': forms.PasswordInput(attrs={'class': 'form-control','placehodelr': 'Entrez votre mot de passe'}),
            #'password': forms.PasswordInput(attrs={'class': 'form-control','placehodelr': 'Confirmez votre mot de passe'}),
        }
    def __init__(self, *args, **kwargs):
        """
        Initialisation personnalisée pour pré-remplir les champs avec les données du modèle.
        """
        super().__init__(*args, **kwargs)

        # Si une instance de `Cours` est fournie, les champs seront automatiquement remplis
        if self.instance and self.instance.pk:
            self.fields['nom'].initial = self.instance.nom
            self.fields['prenom'].initial = self.instance.prenom
            self.fields['email'].initial = self.instance.email
