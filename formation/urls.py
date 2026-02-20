from django.urls import path 
from  . import views 

urlpatterns = [
    path('', views.formation_index , name = "formation_index"),
    path('formations/<int:index>/', views.formation_index, name='formations'),
    path('add/', views.creer_formation, name='add-formation'),
    path('editfrom/<int:pk>/', views.editer_formation, name='fomedit'),
    path('add/<int:pk>/', views.creer_module, name='add-module'),
    path('addc/<int:parent_id>/', views.creer_cours, name='add-cours'),
    path('module/<int:pk>/',views.modules_index, name='module'),
    path('cours/<int:pk>/',views.cours_index, name='cours'),
    path('coursd/<int:pk>/',views.cours_detail, name='coursd'),
    path('couredit/<int:pk>/',views.edit_cours, name='coursedit'),
    path('deletec/<int:pk>/', views.supprimer_cours, name='supprimer_cours'),
    path('addref/<int:cours_id>/', views.ajouter_reference, name='add-ref'),
    path('refedit/<int:pk>/', views.edit_reference, name='refedit'),
    path('gest/', views.gestion_form_mod, name='gestion'),
    path('add-dis/', views.add_discussion, name='discussion'),
    path('detail-dis/<int:pk>/', views. detail_discussion, name='disc-detail'),
]
