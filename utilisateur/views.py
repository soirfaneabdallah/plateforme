from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm  

# Vue pour l'inscription
def register_view(request):
    if request.method == 'GET':
        form = CustomUserCreationForm(request.GET)
        print("OK")
        if form.is_valid():
            print("OK")
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Compte créé pour {username} ! Vous pouvez maintenant vous connecter.")
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()
    return render(request, 'utilisateur/inscription.html', {'form': form})

# Vue pour la connexion
def login_view(request):
    if request.method == 'GET':
        form = AuthenticationForm(request, data=request.GET)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  
            
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'utilisateur/connexion.html', {'form': form})

def logout_view(request):
    logout(request)
    if request.method == 'GET':
        return redirect('index')
    
    return render(request, 'index.html')
def profil(request):
    
    return render(request, 'utilisateur/profil.html')