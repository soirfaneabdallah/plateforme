from django import forms
from django.forms import modelformset_factory
from .models import * 

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['titre', 'description', 'niveau', 'image_couverture']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols':2}),
            'niveau' : forms.Select(attrs={'class': 'form-select'}),
            'image_couverture' : forms.ClearableFileInput(attrs={'class': 'form-control'})
        }
    def __init__(self, *args, **kwargs):
        """
        Initialisation personnalisée pour pré-remplir les champs avec les données du modèle.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['titre'].initial = self.instance.titre
            self.fields['description'].initial = self.instance.description
            self.fields['niveau'].initial = self.instance.niveau
            self.fields['image_couverture'].initial = self.instance.image_couverture
        
class ModulesForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['titre', 'description', 'image_couverture']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control','rows': 4, 'cols':2}),
            'image_couverture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        """
        Initialisation personnalisée pour pré-remplir les champs avec les données du modèle.
        """
        super().__init__(*args, **kwargs)

        # Si une instance de `Cours` est fournie, les champs seront automatiquement remplis
        if self.instance and self.instance.pk:
            self.fields['titre'].initial = self.instance.titre
            self.fields['description'].initial = self.instance.description
            self.fields['image_couverture'].initial = self.instance.image_couverture
class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['titre', 'contenu']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, 'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialisation personnalisée pour pré-remplir les champs avec les données du modèle.
        """
        super().__init__(*args, **kwargs)

        # Si une instance de `Cours` est fournie, les champs seront automatiquement remplis
        if self.instance and self.instance.pk:
            self.fields['titre'].initial = self.instance.titre
            self.fields['contenu'].initial = self.instance.contenu
                  
class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ajouter un commentaire...', 'rows': 1,"col":4}),
        }
class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['titre', 'lien', 'type_reference']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la référence'}),
            'lien': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Lien de la référence'}),
            'type_reference': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'titre': 'Titre',
            'lien': 'Lien',
            'type_reference': 'Type de Référence',
        }
    def __init__(self, *args, **kwargs):
        """
        Initialisation personnalisée pour pré-remplir les champs avec les données du modèle.
        """
        super().__init__(*args, **kwargs)

        # Si une instance de `Cours` est fournie, les champs seront automatiquement remplis
        if self.instance and self.instance.pk:
            self.fields['titre'].initial = self.instance.titre
            self.fields['lien'].initial = self.instance.lien
            self.fields['type_reference'].initial = self.instance.type_reference

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['titre', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la discussion'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description (optionnelle)'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['contenu', 'fichier']
        widgets = {
            'contenu': forms.Textarea(),
            'fichier': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
