from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from .forms import *
import re
from django.utils.safestring import mark_safe

@login_required
def gestion_form_mod(request):
    # Récupération des formations et modules associés à l'utilisateur connecté
    formations = Formation.objects.filter(enseignant=request.user)
    modules = Module.objects.filter(formation__enseignant=request.user)

    contexte = {
        'formations': formations,
        'modules': modules,
    }
    return render(request, 'formation/gestion-formation.html', contexte)
@login_required
def formation_index(request, index=0):
    index = int(index)
    formations = Formation.objects.all()
    list_1 = range(index)
    contexte = {
        "formations" : formations,
        "list_1": list_1,
        "index" : index,
    }
    return render(request, 'formation/index.html', context= contexte)
@login_required
def modules_index(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    modules = formation.modules.all()
    if request.method == 'GET':
        redirect('module',pk=formation.pk)
    contexte = {
        "formations" : formation,
        "modules" : modules,
    }
    return render(request, 'formation/modules.html', context= contexte)

@login_required
def cours_index(request, pk):
    modules = get_object_or_404(Module, pk=pk)
    cours = modules.cours.filter(est_publier = True)
    if request.method == 'GET':
        redirect('cours',pk=modules.pk)
    contexte = {
        "module" : modules,
        "cours" : cours,
    }
    return render(request, 'formation/cours.html', context= contexte)


def est_enseignant(user):
    return user.is_authenticated and user.statut == 'Enseignant'

@login_required
@user_passes_test(est_enseignant)
def creer_formation(request):
    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES)
        if form.is_valid():
            formation = form.save(commit=False)
            formation.enseignant = request.user  # Associe la formation à l'enseignant actuel
            formation.save()
            messages.success(request, 'Formation créée avec succès !')
            return redirect('formations', index=formation.pk)
    else:
        form = FormationForm()
    return render(request, 'formation/add_formation.html', {'form': form})

# Vue pour éditer une formation (réservée aux enseignants)
@login_required
@user_passes_test(est_enseignant)
def editer_formation(request, pk):
    formation = get_object_or_404(Formation, pk=pk, enseignant=request.user)  # Vérifie que l'enseignant est propriétaire
    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES, instance=formation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Formation mise à jour avec succès !')
            return redirect('formation_index')
    else:
        form = FormationForm(instance=formation)
    return render(request, 'formation/add_formation.html', {'form': form,'edit':True})

# Vue pour supprimer une formation (réservée aux enseignants)
@login_required
@user_passes_test(est_enseignant)
def supprimer_formation(request, pk):
    formation = get_object_or_404(Formation, pk=pk, enseignant=request.user)
    if request.method == 'POST':
        formation.delete()
        messages.success(request, 'Formation supprimée avec succès !')
        return redirect('formation_liste')
    return render(request, 'formation/supprimer_formation.html', {'formation': formation})



@login_required
@user_passes_test(est_enseignant)
def creer_module(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        form = ModulesForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.formation = formation
            module.save()  # L'ordre est automatiquement calculé dans le modèle
            messages.success(request, 'Module créé avec succès !')
            return redirect('module', pk=formation.pk)
    else:
        form = ModulesForm()
    return render(request, 'formation/add-module.html', {'form': form, 'formation': formation})


def creer_cours(request,  parent_id=None):
    
    parent = get_object_or_404(Module, pk=parent_id)
    titre = f"Cours pour le Module : {parent.titre}"
    elements = parent.cours.all()  # Récupérer tous les cours du module
    form = CoursForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cours = form.save(commit=False)
        cours.module = parent  # Associer le cours au module
        cours.save()
        messages.success(request, "Cours ajouté avec succès !")
        return redirect('coursd',  pk=cours.pk)

    contexte =  {
    'form': form,
    'titre': titre,
    'elements': elements,
    'cours': parent,
    
     }
    return render(request, 'formation/add-cours.html', context= contexte)


def formater_contenu(contenu_brut):
    # Gestion des titres
    contenu_brut = re.sub(
        r'h1"""(.*?)"""',
        r'<h1 style="color: #2c3e50; font-size: 2.5em;">\1</h1>',
        contenu_brut,
        flags=re.DOTALL,
    )
    contenu_brut = re.sub(
        r'h2"""(.*?)"""',
        r'<h2 style="color: #34495e; font-size: 2em; ">\1</h2>',
        contenu_brut,
        flags=re.DOTALL,
    )
    contenu_brut = re.sub(
        r'h3"""(.*?)"""',
        r'<h3 style="color: #7f8c8d; font-size: 1.5em;">\1</h3>',
        contenu_brut,
        flags=re.DOTALL,
    )

     # Gestion des blocs de code Python avec bouton de copie
    def ajouter_bouton_copie(match):
        code = match.group(1)
        return f"""
        <div class="code-container position-relative">
            <button class="copy-btn btn btn-sm btn-light position-absolute top-0 end-0 m-2" onclick="copierCode(this)">
                <i class="bi bi-clipboard"></i>
            </button>
            <pre><code class="language-python">{code}</code></pre>
        </div>
        """

    contenu_brut = re.sub(
        r'python"""(.*?)"""',
        ajouter_bouton_copie,
        contenu_brut,
        flags=re.DOTALL
    )
    # Gestion des formules mathématiques (encadrées par $$)
    contenu_brut = re.sub(
        r'\$\$(.*?)\$\$',
        r'<div class="mathjax">\1</div>',
        contenu_brut,
        flags=re.DOTALL,
    )

    # Gestion des listes
    contenu_brut = re.sub(
        r'ul"""(.*?)"""',
        r'<ul>\1</ul>',
        contenu_brut,
        flags=re.DOTALL,
    )
    contenu_brut = re.sub(
        r'li"""(.*?)"""',
        r'<li>\1</li>',
        contenu_brut,
        flags=re.DOTALL,
    )

    # Gestion des couleurs (balise personnalisée : color""[couleur]texte"")
    contenu_brut = re.sub(
        r'color"""\[(.*?)\](.*?)"""',
        r'<span style="color:\1;">\2</span>',
        contenu_brut,
    )

    # Gestion des textes en gras
    contenu_brut = re.sub(
        r'bold"""(.*?)"""',
        r'<strong>\1</strong>',
        contenu_brut,
    )

    # Gestion des textes en italique
    contenu_brut = re.sub(
        r'italic"""(.*?)"""',
        r'<em>\1</em>',
        contenu_brut,
    )

    # Gestion des textes soulignés
    contenu_brut = re.sub(
        r'underline"""(.*?)"""',
        r'<u>\1</u>',
        contenu_brut,
    )

    # Marque le contenu comme sûr pour un affichage HTML
    return mark_safe(contenu_brut)


def handle_comment_submission(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id)
    if request.method == 'POST':
        form_commentaire = CommentaireForm(request.POST)
        
        if form_commentaire.is_valid():
            commentaire = form_commentaire.save(commit=False)
            commentaire.utilisateur = request.user
            commentaire.cours = cours
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Commentaire.objects.get(pk=parent_id)
                    commentaire.parent = parent_comment
                except Commentaire.DoesNotExist:
                    form_commentaire.add_error(None, "Le commentaire parent n'existe pas.") 
                    return form_commentaire, None
            commentaire.save()
            return form_commentaire, redirect('coursd', pk=cours.pk) 
    else:
      form_commentaire = CommentaireForm()
    return form_commentaire, None
def handle_quiz_submission(request, quiz):
    questions = quiz.questions.all()
    reponses_utilisateur = {}
    score = 0

    for question in questions:
        reponse = request.POST.get(f'question_{question.id}')
        reponses_utilisateur[question.id] = reponse

    for question in questions:
        if question.type_question == 'choix_multiple':
            option_correcte = question.options.filter(est_correct=True).first()
            if option_correcte and str(option_correcte.id) == reponses_utilisateur.get(str(question.id)):
                score += 1

    return score, redirect('coursd', pk=quiz.cours_set.first().pk)
@login_required
def cours_detail(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    contenu_formate = formater_contenu(cours.contenu)
    commentaires = cours.commentaires.filter(parent__isnull=True).order_by('-date_creation')
    form_commentaire = CommentaireForm()
    score = None
    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            
            if request.method == 'POST':
              form_commentaire, redirection = handle_comment_submission(request, cours.pk)
            if redirection:
                messages.success(request, "Votre commentaire a été ajouté avec succès.")
                return redirection
            


    contexte = {
        'cours': cours,
        'contenu_formater': contenu_formate,
        'commentaires': commentaires,
        'form_commentaire': form_commentaire,
        'score': score,
    }

    return render(request, 'formation/cours-detail.html', contexte)
def liker_commentaire(request, commentaire_id):
    commentaire = get_object_or_404(Commentaire, id=commentaire_id)
    if request.user in commentaire.likes.all():
        commentaire.likes.remove(request.user)
    else:
        commentaire.likes.add(request.user)
    return redirect('detail_cours', cours_id=commentaire.cours.id)



def edit_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    if request.method == 'POST':
        # Pré-remplir avec les données envoyées dans le POST
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            cours.titre = form.cleaned_data['titre']
            cours.contenu = form.cleaned_data['contenu']
            cours.save()
            messages.success(request, 'Cours éditer avec succès !')
            return redirect('coursd', pk=cours.pk)
    else:
        form = CoursForm(instance=cours)
    contexte = {
        'edite': True,
        'cours' : cours,
        'formetid': form,
    }
    return render(request,'formation/add-cours.html',context=contexte)
@login_required
def supprimer_cours(request, pk):
    """
    Supprime un cours après confirmation par l'utilisateur.
    """
    cours = get_object_or_404(Cours, pk=pk)
    cours.delete()
    return render(request,'formation/Cours.html')
def ajouter_reference(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id)

    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            reference = form.save(commit=False)
            reference.cours = cours
            reference.save()
            messages.success(request, "Référence ajoutée avec succès !")
            return redirect('coursd', pk=cours_id)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ReferenceForm()

    return render(request, 'formation/add-ref.html', {'form': form, 'cours': cours})
def edit_reference(request, pk):
    reference = get_object_or_404(Reference, pk=pk)
    if request.method == 'POST':
        # Pré-remplir avec les données envoyées dans le POST
        form = ReferenceForm(request.POST, instance=reference)
        if form.is_valid():
            reference.titre = form.cleaned_data['titre']
            reference.lien = form.cleaned_data['lien']
            reference.type_reference = form.cleaned_data['type_reference']
            reference.save()
            messages.success(request, 'Référence éditer avec succès !')
            return redirect('coursd', pk=reference.cours.pk)
    else:
        form = ReferenceForm(instance=reference)
    contexte = {
        'edit': True,
        'reference' : reference,
        'form': form,
    }
    return render(request,'formation/add-ref.html',context=contexte)
@login_required
def add_discussion(request):
    """
    Vue pour créer une nouvelle discussion.

    Args:
        request: Objet de requête HTTP.

    Returns:
        HttpResponse: Page HTML pour créer une discussion.
    """
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.createur = request.user
            discussion.save()
            messages.success(request, "Discussion créée avec succès !")
            return redirect('disc-detail')
        else:
            messages.error(request, "Erreur lors de la création de la discussion. Veuillez corriger les erreurs.")
    else:
        form = DiscussionForm()

    return render(request, 'formation/add-discussion.html', {'form': form})

@login_required
def detail_discussion(request, pk):
    # Récupère toutes les discussions pour la navigation
    discussions = Discussion.objects.all()

    # Récupère la discussion actuelle et ses messages
    discussion = get_object_or_404(Discussion, pk=pk)
    messages_list = Message.objects.filter(discussion=discussion, parent__isnull=True).prefetch_related('replies')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)

        if form.is_valid():
            # Crée un message ou une réponse
            message = form.save(commit=False)
            message.auteur = request.user
            message.discussion = discussion

            # Vérifie si c'est une réponse (champ hidden "reply_to" dans le formulaire)
            reply_to_id = request.POST.get('reply_to')
            if reply_to_id:
                parent_message = get_object_or_404(Message, pk=reply_to_id)
                message.parent = parent_message

            message.save()
            return redirect('disc-detail', pk=discussion.pk)

    else:
        form = MessageForm()

    return render(request, 'formation/disc-detail.html', {
        'discussions': discussions,
        'discussion': discussion,
        'form': form,
        'messages': messages_list,  # Liste des messages principaux avec leurs réponses
    })
