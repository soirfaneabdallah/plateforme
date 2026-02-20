from django import forms
from .models import *

class ExerciceForm(forms.ModelForm):
    class Meta:
        model = Exercice
        fields = ['titre', 'description', 'ennoce', 'solution_attendue', 'code_initial', 'niveau']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre de l’exercice...'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Décrivez brièvement l’exercice...'
            }),
            'ennoce': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Énoncé de l’exercice...'
            }),
            'solution_attendue': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': "Indiquez la solution attendue de l’exercice..."
            }),
            'code_initial': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': "Ajoutez un exemple de code ou une base pour aider l’étudiant à démarrer..."
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class SoumissionForm(forms.ModelForm):
    class Meta:
        model = Soumission
        fields = ['code_soumis']
        widgets = {
            'code_soumis': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Écrivez votre code ici...',
                'rows': 10,
                'style': 'font-family: monospace;'
            }),
        }

class OutilForm(forms.ModelForm):
    class Meta:
        model = Outil
        fields = ['nom', 'description', 'categorie', 'est_public']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Entrez le nom de l\'outil',
                'aria-label': 'Nom de l\'outil',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Décrivez l\'outil (optionnel)',
                'aria-label': 'Description',
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Catégorie',
            }),
            'est_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input', 
                'aria-label': 'Rendre cet outil public',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['nom'].initial = self.instance.nom
            self.fields['description'].initial = self.instance.description
            self.fields['categorie'].initial = self.instance.categorie
            self.fields['est_public'].initial = self.instance.est_public
