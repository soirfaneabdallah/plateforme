from django.contrib.auth.models import AbstractUser
from django.db import models
#from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

class Utilisateur(AbstractUser):
    # Champs supplémentaires
    nom = models.CharField("Entrez votre nom", max_length=150, unique=False)
    prenom = models.CharField("Entrez votre prénom", max_length=150,unique=False)
    email = models.EmailField("Entrez votre email", unique=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    # Champ de statut avec une valeur par défaut "Etudiant"
    STATUT_CHOICES = [
        ('Etudiant', 'Etudiant'),
        ('Enseignant', 'Enseignant'),
        ('Exclus',"Exclus")
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Etudiant')

    # Définir le champ d'authentification comme étant l'email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L’adresse email doit être renseignée'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True'))

        return self.create_user(email, password, **extra_fields)
