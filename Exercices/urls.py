from django.urls import path 
from  . import views 

urlpatterns = [
   path('exe/', views.exercice_index,name="index-exercice"),
   path('add/',views.add_exercice,name="ajout-exercice"),
   path('detail/<int:pk>/',views.detail_exercice, name="detail-exercice"),
   path('outils/',views.liste_outils, name="list-outils"),
   path('addoutils/',views.add_outil, name="add-outils"),
   path('outils/modifier/<int:outil_id>/', views.modifier_outil, name='modifier_outil'),
   path('outils/supprimer/<int:outil_id>/', views.supprimer_outil, name='supprimer_outil'),
   path('outils/rendre_public/<int:outil_id>/', views.rendre_public, name='rendre_public'),
   path('outils/retirer_public/<int:outil_id>/', views.retirer_public, name='retirer_public'),
   
]