import subprocess
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib import messages
import sys
from .models import *
def get_stars(level):
    return ["fill" if i < level else "empty" for i in range(3)]
@login_required
def exercice_index(request):
    debutant = Exercice.objects.filter(niveau='débutant')
    intermediaire = Exercice.objects.filter(niveau='intermédiaire')
    avance = Exercice.objects.filter(niveau='avancé')
    # Obtenir toutes les soumissions validées pour cet utilisateur
    soumissions_validees = Soumission.objects.filter(etudiant=request.user, est_correct=True).values_list('exercice_id', flat=True)

    # Ajouter une clé pour indiquer si chaque exercice est validé
    debutant = [
        {'exercice': ex, "stars": get_stars(1), 'valide': ex.id in soumissions_validees} for ex in debutant
    ]
    intermediaire = [
        {'exercice': ex, "stars": get_stars(2), 'valide': ex.id in soumissions_validees} for ex in intermediaire
    ]
    avance = [
        {'exercice': ex, "stars": get_stars(3), 'valide': ex.id in soumissions_validees} for ex in avance
    ]

    contexte = {
        'debutant': debutant,
        'intermediaire': intermediaire,
        'avance': avance,
    }
    return render(request, 'exercices/list-exercice.html', context=contexte)

def add_exercice(request):
    if request.method == 'POST':
        form = ExerciceForm(request.POST)
        if form.is_valid():
            exercice = form.save(commit=False)
            exercice.enseignant = request.user
            exercice.save()
            return redirect('index-exercice')
    else:
        form = ExerciceForm()
    return render(request, 'exercices/add-exercice.html', {'form': form})

def evaluer_soumission(soumission):
    try:
        # Exécute le code soumis par l'étudiant
        result = subprocess.run(
            [sys.executable, '-c', soumission.code_soumis],
            capture_output=True,
            text=True,
            timeout=5  # Limite de temps pour éviter les boucles infinies
        )
        # Stocke la sortie
        soumission.sortie = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        # Compare la sortie avec la solution attendue
        soumission.est_correct = soumission.sortie == soumission.exercice.solution_attendue
        soumission.save()
        return soumission.est_correct
    except Exception as e:
        soumission.sortie = str(e)
        soumission.save()
        return False

def valide_exrcice(etudiant,id_exercice):
    exercice = get_object_or_404(Exercice, pk=id_exercice)
    soumission = Soumission.objects.filter(etudiant=etudiant,exercice=exercice)
    if soumission and soumission.est_correct:
        return True
    return False
def evaluer_soumission(soumission):
    """
    Évalue la soumission et met à jour le modèle `Resultat`.

    Args:
        soumission (Soumission): La soumission à évaluer.

    Returns:
        bool: Indique si l'exercice a été validé.
    """
    exercice = soumission.exercice
    # Exemple simple : comparer la sortie à une sortie attendue
    attendu = exercice.solution_attendue.strip()
    soumis = soumission.sortie.strip() if soumission.sortie else ""

    valide = soumis == attendu
    score = 100.0 if valide else 0.0
    feedback = "Bravo, vous avez réussi l'exercice !" if valide else "Essayez encore, votre sortie est incorrecte."
    soumission.est_correct = True if valide else False
    soumission.save()
        

    # Mettre à jour ou créer un résultat
    Resultat.objects.update_or_create(
        soumission=soumission,
        defaults={
            'score': score,
            'feedback': feedback
        }
    )

    return valide
def mettre_a_jour_progression(utilisateur, exercice_valide):
    """
    Met à jour la progression de l'utilisateur.

    Args:
        utilisateur (User): L'utilisateur concerné.
        exercice_valide (bool): Indique si l'exercice a été validé.

    Returns:
        None
    """
    progression, _ = Progression.objects.get_or_create(etudiant=utilisateur)

    # Mettre à jour les tentatives
    progression.exercices_tentatives += 1

    # Mettre à jour les réussites uniquement si l'exercice est validé
    if exercice_valide:
        progression.exercices_reussis += 1

    progression.save()

@login_required
def detail_exercice(request, pk):
    """
    Vue pour afficher les détails d'un exercice et gérer les soumissions des étudiants.

    Args:
        request: Objet de requête HTTP.
        pk: Identifiant de l'exercice.

    Returns:
        HttpResponse: Page HTML avec les détails de l'exercice et les résultats.
    """
    exercice = get_object_or_404(Exercice, pk=pk)
    soumissions = Soumission.objects.filter(exercice=exercice)
    soumission = Soumission.objects.filter(etudiant=request.user, exercice=exercice).first()

    if request.method == 'POST' and "executer" in request.POST:
        code = request.POST.get('code_soumis')

        if soumission:
            # Mise à jour de la soumission existante
            soumission.code_soumis = code
        else:
            # Création d'une nouvelle soumission
            soumission = Soumission.objects.create(
                exercice=exercice,
                etudiant=request.user,
                code_soumis=code
            )

        try:
            # Exécution du code soumis dans un environnement isolé
            result = subprocess.run(
                [sys.executable, '-c', code],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                soumission.sortie = result.stdout
                soumission.erreur = None
            else:
                soumission.sortie = None
                soumission.erreur = result.stderr

        except subprocess.TimeoutExpired:
            soumission.sortie = None
            soumission.erreur = "Erreur : le code a dépassé le temps limite d'exécution."
        except Exception as e:
            soumission.sortie = None
            soumission.erreur = f"Erreur inattendue : {str(e)}"

        # Sauvegarder la soumission
        soumission.save()

        # Évaluer la soumission et mettre à jour le résultat
        exercice_valide = evaluer_soumission(soumission)

        # Mettre à jour la progression de l'étudiant
        mettre_a_jour_progression(request.user, exercice_valide)

        # Message de succès ou d'échec
        if exercice_valide:
            messages.success(request, "Félicitations ! Vous avez réussi cet exercice.")
            
        else:
            messages.error(request, "Votre soumission est incorrecte. Essayez encore !")

    if request.method == "POST" and "partager" in request.POST:
        soumission.partager = True
        soumission.save()
        messages.success(request, "Merci de partager votre expérience avec la communauté !")
        return redirect("detail-exercice", pk=exercice.pk)

    contexte = {
        'exercice': exercice,
        'soumission': soumission,
        'soumissions': soumissions,
    }
    return render(request, 'exercices/detail-exercice.html', contexte)


@login_required
def add_outil(request):
    if request.method == 'POST':
        form = OutilForm(request.POST)
        if form.is_valid():
            outil = form.save(commit=False)
            outil.utilisateur = request.user
            outil.save()
            messages.success(request, "Outil ajouté avec succès!")
            return redirect('list-outils')
    else:
        form = OutilForm()
    
    return render(request, 'exercices/add-outils.html', {'form': form})

@login_required
def liste_outils(request):
    outils_prives = Outil.objects.filter(utilisateur=request.user)
    outils_publics = Outil.objects.filter(est_public=True)
    return render(request, 'exercices/outils.html', {
        'outils_prives': outils_prives,
        'outils_publics': outils_publics
    })
@login_required
def modifier_outil(request, outil_id):
    """
    Vue pour modifier un outil spécifique.
    """
    outil = get_object_or_404(Outil, pk=outil_id, utilisateur=request.user)
    if request.method == 'POST':
        form = OutilForm(request.POST, instance=outil)
        if form.is_valid():
            form.save()
            return redirect('list-outils')
    else:
        form = OutilForm(instance=outil)
    edit = True

    return render(request, 'exercices/add-outils.html',
                  {'form': form, 'outil': outil, "edit" : edit})


@login_required
def supprimer_outil(request, outil_id):
    """
    Vue pour supprimer un outil.
    """
    outil = get_object_or_404(Outil, id=outil_id, utilisateur=request.user)
    outil.delete()
    return redirect('list-outils')


@login_required
def rendre_public(request, outil_id):
    """
    Vue pour rendre un outil public.
    """
    outil = get_object_or_404(Outil, id=outil_id, utilisateur=request.user)
    outil.est_public = True
    outil.save()
    return redirect('list-outils')


@login_required
def retirer_public(request, outil_id):
    """
    Vue pour retirer un outil du public.
    """
    outil = get_object_or_404(Outil, id=outil_id, utilisateur=request.user)
    outil.est_public = False
    outil.save()
    return redirect('list-outils')