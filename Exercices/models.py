from django.db import models
from django.contrib.auth import get_user_model
from formation.views import formater_contenu
User = get_user_model()
class Exercice(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField(max_length= 300)
    ennoce = models.TextField(default="")
    code_initial = models.TextField(blank=True, null=True,)  
    solution_attendue = models.TextField(max_length= 300) 
    date_creation = models.DateTimeField(auto_now_add=True)
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exercices")
    NIVEAU_CHOICES = [
        ("débutant", 'Débutant'),
        ('intermédiaire', 'Intermédiaire'),
        ('avancé', 'Avancé')
    ]
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES,default='Débutant')
    
    def __str__(self):
        return self.titre
     
class Soumission(models.Model):
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="soumissions")
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name="soumissions")
    code_soumis = models.TextField()  
    sortie = models.TextField(blank=True, null=True)  
    date_soumission = models.DateTimeField(auto_now_add=True)
    erreur= models.TextField(null=True, blank=True)
    est_correct = models.BooleanField(default=False)
    partager = models.BooleanField(default=False) 

    def __str__(self):
        return f"Soumission par {self.etudiant.username} pour {self.exercice.titre}"
    def est_valide(self):
        soumission = Soumission.objects.filter(self.etudiant,self.exercice)
        if soumission and soumission.est_correct:
           return True
        return False

class Resultat(models.Model):
    soumission = models.OneToOneField(Soumission, on_delete=models.CASCADE, related_name="resultat")
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Score sur 100
    feedback = models.TextField(blank=True, null=True)  # Optionnel : commentaires automatiques sur la soumission

    def __str__(self):
        return f"Résultat pour {self.soumission.etudiant.username} - {self.soumission.exercice.titre}"
class Progression(models.Model):
    etudiant = models.OneToOneField(User, on_delete=models.CASCADE, related_name="progression")
    exercices_reussis = models.PositiveIntegerField(default=0)
    exercices_tentatives = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Progression de {self.etudiant.username}"
class Outil(models.Model):
    CATEGORIES = [
        ('IDE', 'Environnement de développement intégré'),
        ('LIB', 'Bibliothèque/Framework'),
        ('DB', 'Base de données'),
        ('OTH', 'Autres'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="outils")
    nom = models.CharField(max_length=255)  # Nom de l'outil
    description = models.TextField(blank=True, null=True)  # Description de l'outil
    categorie = models.CharField(max_length=3, choices=CATEGORIES, default='OTH')  # Catégorie de l'outil
    est_public = models.BooleanField(default=False)  # Indique si l'outil est public ou privé
    date_ajout = models.DateTimeField(auto_now_add=True)  # Date d'ajout de l'outil
    
    def __str__(self):
        return f"{self.nom} ({'Public' if self.est_public else 'Privé'})"
    def formater(self):
        self.description=formater_contenu(self.description)
        return self.description
        