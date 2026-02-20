# models.py
from django.utils import timezone
from django.db import models
from utilisateur.models import Utilisateur
from uuid import uuid4  # Pour générer des noms d'images aléatoires
import os
import shutil

def image_upload_to(instance, filename):
    """ Génère un chemin de sauvegarde basé sur la classe confirmée ou prédite """
    classe = instance.classe if instance.classe_corrigee == " " else instance.classe_corrigee
    unique_filename = f"{uuid4()}_{filename}"
    return os.path.join('predictions', classe, unique_filename)

class Predictions(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    nom = models.CharField(max_length = 100)
    classe = models.CharField(max_length = 50, blank=True)
    precision = models.IntegerField(default = 0.0)
    anomalie_detectee = models.BooleanField(null = True)  # Résultat du modèle
    anomalie_confirmee = models.BooleanField(null = True)  # Confirmation utilisateur
    classe_corrigee = models.CharField(max_length=50, blank = True)  # Classe choisie par l’utilisateur si correction
    image = models.ImageField(upload_to= image_upload_to, blank = True)
    date_prediction = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Prediction {self.nom} - {self.utilisateur.username}"

    def save(self, *args, **kwargs):
        
        if not self.nom:
            self.nom = str(uuid4())
        super().save(*args, **kwargs)
        
    def update_image_path(self):
        """Déplace l'image si la classe confirmée est différente de la classe prédite."""
        # Nouveau chemin basé sur la classe confirmée
        new_path = image_upload_to(self, os.path.basename(self.image.name))
        old_path = self.image.path
        # Mettre à jour le champ `image` dans le modèle
        self.image.name = new_path
        self.save()
        # Déplacer physiquement le fichier
        os.makedirs(os.path.dirname(self.image.path), exist_ok=True)
        shutil.move(old_path, self.image.path)
