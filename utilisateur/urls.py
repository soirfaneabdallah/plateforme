from django.urls import path
from .views import register_view, login_view, logout_view,profil

urlpatterns = [
    path('register/', register_view, name='inscription'),
    path('login/', login_view, name='connexion'),
    path('', logout_view, name='logout'),
    path('profil', profil, name='profil'),
]
