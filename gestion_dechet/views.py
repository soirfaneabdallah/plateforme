from django.shortcuts import render
from prediction.models import Predictions
from utilisateur.models import Utilisateur
from Exercices.models import Soumission, Exercice
from django.db.models import F


def index(request):
   
   nombre_exercices = Exercice.objects.all().count()
   enseigants = Utilisateur.objects.filter(statut="Enseignant")
   predictions_totales = Predictions.objects.all().count()
   bonne_predictions = Predictions.objects.filter(classe= F("classe_corrigee")).count()
   fausse_predictions = Predictions.objects.exclude(classe= F("classe_corrigee")).count()
   anomalies = Predictions.objects.filter(anomalie_detectee= F("anomalie_confirmee")).count()
   pourcentages_valides = ( bonne_predictions / predictions_totales )*100 if predictions_totales > 0 else 0
   pourcentages_non_valides = (fausse_predictions / predictions_totales)*100 if predictions_totales > 0 else 0
   pourcentages_anomalies = (anomalies / predictions_totales)*100 if predictions_totales > 0 else 0
   contexte = {
      "bonne_predictions" : bonne_predictions,
      "pourcentages_valides" : round(pourcentages_valides,2),
      "fausse_predictions" : fausse_predictions,
      "pourcentages_non_valides" : round(pourcentages_non_valides, 2),
      "anomalies": anomalies,
      "pourcentages_anomalies"  : round(pourcentages_anomalies, 2),
      "enseigants" : enseigants,
     
      "nombre_exercices": nombre_exercices,
      
   }
   
   return render(request, "index.html", context = contexte)


def custom_404_view(request, exception):
    """
    Vue personnalisée pour l'erreur 404.
    """
    return render(request, '404.html', status=404)
def faq(request):
   return render(request, 'faq.html')