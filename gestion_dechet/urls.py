
from django.contrib import admin
from django.urls import path , include
from gestion_dechet import settings
from  .views import index, faq
from django.conf.urls.static import static
from gestion_dechet import settings
urlpatterns = [
    path('',index ,name = "index"),
    path("page/", admin.site.urls),
    path("faq/", faq, name = "faq"),
    path("utilisateur/", include("utilisateur.urls"), name = "utilisateur"),
    path("prediction/", include("prediction.urls"), name = "prediction"),
    path("formation/", include("formation.urls"), name = "formation"),
    path("exercice/", include("Exercices.urls"), name = "exercices"),
] + static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )



# Associer la vue 404
handler404 = 'gestion_dechet.views.custom_404_view'
