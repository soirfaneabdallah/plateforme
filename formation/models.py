from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image
User = get_user_model()

# Model pour les formations
class Formation(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    NIVEAU_CHOICES = [
        ('débutant', 'Débutant'),
        ('intermédiaire', 'Intermédiaire'),
        ('avancé', 'Avancé')
    ]
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    date_creation = models.DateTimeField(default=timezone.now)
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="formations")
    image_couverture = models.ImageField(upload_to='formations/couvertures/', blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        img_path = self.image_couverture.path
        img = Image.open(img_path)
        max_size = (200, 200)  
        img.resize(max_size)
        img.save(img_path)
            
    def __str__(self):
        return self.titre

# Model pour les modules
class Module(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="modules")
    ordre = models.PositiveIntegerField()
    image_couverture = models.ImageField(upload_to='formations/couvertures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.titre} ({self.formation.titre})"
    
    def save(self, *args, **kwargs):
            # Si l'ordre n'est pas spécifié, calculez l'ordre automatiquement
        if self.ordre is None:
            max_ordre = Module.objects.filter(formation=self.formation).aggregate(models.Max('ordre'))['ordre__max']
            self.ordre = (max_ordre or 0) + 1
        super().save(*args, **kwargs)

# Model pour les cours
class Cours(models.Model):
    titre = models.CharField(max_length=255)
    contenu =   models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="cours")
    ordre = models.PositiveIntegerField()
    est_publier = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Si l'ordre n'est pas défini, le calculer automatiquement
        if self.ordre is None:
            dernier_ordre = Cours.objects.filter(module=self.module).aggregate(models.Max('ordre'))['ordre__max']
            self.ordre = (dernier_ordre or 0) + 1
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.titre} ({self.module.titre})"


class Progression(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progressions")
    lecon = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="progressions")
    STATUT_CHOICES = [
        ('commencee', 'Commencée'),
        ('completee', 'Complétée')
    ]
    status = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_derniere_maj = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progression de {self.utilisateur.username} dans {self.lecon.titre}"

# Model pour les récompenses
class Recompense(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    conditions = models.TextField()  # Peut être utilisé pour définir des critères d'obtention

    def __str__(self):
        return self.titre

# Model pour les commentaires
class Commentaire(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentaires")
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="commentaires")
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reponses')
    approuve = models.BooleanField(default=True)  # Modération
    likes = models.ManyToManyField(User, related_name='commentaires_likes', blank=True,default="")


    def __str__(self):
        return f"Commentaire de {self.utilisateur.username} sur {self.cours.titre}"

    @property
    def est_reponse(self):
        return self.parent is not None

    def get_nombre_likes(self):
        return self.likes.count()
    def nombre_de_reponses(self):
        
        count = self.reponses.count()
        for reponse in self.reponses.all():
            count += reponse.nombre_de_reponses()
        return count
    
class Reference(models.Model):
    TYPES = [
        ('video', 'Vidéo'),
        ('document', 'Document'),
        ('lien_externe', 'Lien Externe'),
    ]
    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name="references",
        help_text="Cours associé à la référence"
    )
    titre = models.CharField(max_length=255, help_text="Titre de la référence")
    lien = models.URLField(max_length=500, help_text="URL de la référence")
    type_reference = models.CharField(max_length=20, choices=TYPES, help_text="Type de référence")
    date_creation = models.DateTimeField(default=timezone.now, help_text="Date et heure de création de la référence")

    def __str__(self):
        return f"{self.titre} ({self.get_type_reference_display()})"

class Discussion(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussions")

    def __str__(self):
        return self.titre

class Message(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="messages")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    contenu = models.TextField(null=True, blank=True)
    fichier = models.FileField(upload_to="messages/fichiers/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    def __str__(self):
        return f"Message de {self.auteur.username} dans {self.discussion.titre}"