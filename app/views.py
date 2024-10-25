from itertools import chain
from django.db.models import CharField, Value

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import UserSearchForm, TicketForm, CritiqueForm
from .models import Ticket, Critique, Profile


def login_user(request):
    if request.user.is_authenticated:
        return redirect('flux')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('flux')  # Redirect to a success page.
        else:
            messages.success(request, "There Was An Error Logging In, Try Again...")
            return redirect('login')  # Return an 'invalid login' error message.
    else:
        return render(request, '../templates/login/login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('flux')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration Successful !")
            return redirect('flux')
    else:
        form = UserCreationForm()
        form.fields['username'].widget.attrs.update({'class': 'form-control'})
        form.fields['password1'].widget.attrs.update({'class': 'form-control'})
        form.fields['password2'].widget.attrs.update({'class': 'form-control'})
    return render(request, '../templates/register/register.html', {'form': form})


@login_required
def flux(request):
    profile = request.user.profile

    # Récup les utilisateurs suivis par l'utilisateur co
    followed_users = profile.subscriptions.all()

    # Récup les profils des utilisateurs suivis
    # .exclude(id=profile.id) permet de le pas avoir de doublon si jamais l'utilisateur se suit lui même
    followed_profiles = Profile.objects.filter(user__in=followed_users).exclude(id=profile.id)

    # Récupérer les tickets des utilisateurs suivis
    followed_users_tickets = Ticket.objects.filter(user__in=followed_profiles)

    # Récupérer les critiques des utilisateurs suivis
    followed_users_critique = Critique.objects.filter(user__in=followed_profiles)

    # Tickets et critiques de l'utilisateur co
    my_tickets = Ticket.objects.filter(user=profile)
    my_critiques = Critique.objects.filter(user=profile)

    # Critiques en réponse aux billets de l'utilisateur connecté, sans inclure ses propres critiques
    critiques_on_my_tickets = Critique.objects.filter(ticket__user=profile).exclude(user=profile)

    # Annoter chaque queryset pour distinguer tickets / critiques
    followed_users_tickets = followed_users_tickets.annotate(content_type=Value('TICKET', CharField()))
    my_tickets = my_tickets.annotate(content_type=Value('TICKET', CharField()))
    followed_users_critique = followed_users_critique.annotate(content_type=Value('CRITIQUE', CharField()))
    my_critiques = my_critiques.annotate(content_type=Value('CRITIQUE', CharField()))
    critiques_on_my_tickets = critiques_on_my_tickets.annotate(content_type=Value('CRITIQUE', CharField()))

    # Combiner et trier les billets et critiques
    posts = sorted(
        chain(followed_users_tickets, followed_users_critique, my_tickets, my_critiques, critiques_on_my_tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    print(followed_users_tickets)
    print(followed_users_critique)
    print(my_tickets)
    print(my_critiques)
    print(critiques_on_my_tickets)

    return render(request, '../templates/flux/flux.html', context={'posts': posts})

@login_required
def subscription(request):
    search_users = None
    profile = request.user.profile

    if request.method == 'GET' and request.GET:  # Vérifier s'il y a des paramètres GET car utilisation automatique de la methode GET à la génération de la page
        form_search = UserSearchForm(request.GET)
        if form_search.is_valid():
            username = form_search.cleaned_data['username']
            search_users = User.objects.filter(username__icontains=username)
    else:
        form_search = UserSearchForm()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user_to_subscribe = get_object_or_404(User, id=user_id)

            if user_to_subscribe in profile.subscriptions.all():
                profile.subscriptions.remove(user_to_subscribe)  # Désabonnement
            else:
                profile.subscriptions.add(user_to_subscribe)  # Abonnement
    return render(request, '../templates/subscription/subscription.html',
                  {'form_search': form_search, 'search_users': search_users, 'user_profile': profile})


@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)  # Ne sauvegarde pas encore dans la base de données
            ticket.user_id = request.user.profile.id  # Récupère l'ID du profil de l'utilisateur actuel
            ticket.save()  # Maintenant sauvegarde le ticket
            messages.success(request, 'Votre ticket a été envoyé avec succès !')  # Message de succès
            return redirect('create_ticket')
    else:
        form = TicketForm()

    return render(request, '../templates/ticket/ticket.html', {'form': form})


@login_required
def create_ticket_critique(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        critique_form = CritiqueForm(request.POST, request.FILES)
        if ticket_form.is_valid() and critique_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user_id = request.user.profile.id
            ticket.save()
            critique = critique_form.save(commit=False)
            critique.user_id = request.user.profile.id
            critique.ticket = ticket
            critique.save()
            messages.success(request, 'Votre Ticket & Critique ont été envoyé avec succès !')
            return redirect('create_ticket_critique')
    else:
        ticket_form = TicketForm()
        critique_form = CritiqueForm()
    return render(request, '../templates/ticket_critique/ticket_critique.html', {
        'ticket_form': ticket_form,
        'critique_form': critique_form
    })


@login_required
def my_posts(request):
    profile = request.user.profile

    if request.method == 'POST':
        ticket_id = request.POST.get('delete_ticket_id')  # Récupère l'id du ticket via le champ du formulaire
        critique_id = request.POST.get('delete_critique_id')

        if ticket_id:
            ticket_to_delete = get_object_or_404(Ticket, id=ticket_id, user=profile)  # Récupère le ticket en db
            ticket_to_delete.delete()  # Supprime le ticket en db

        if critique_id:
            critique_to_delete = get_object_or_404(Critique, id=critique_id, user=profile)
            critique_to_delete.delete()  # Supprime la critique en db

    # Récupérer à nouveau les tickets et critiques après une éventuelle suppression
    my_tickets = Ticket.objects.filter(user=profile)
    my_critiques = Critique.objects.filter(user=profile)

    return render(request, '../templates/my_posts/my_posts.html', {
        'my_tickets': my_tickets,
        'my_critiques': my_critiques,
    })


@login_required
def modify_ticket(request, ticket_id):
    profile = request.user.profile
    ticket = get_object_or_404(Ticket, id=ticket_id,
                               user=profile)  # Assure que l'utilisateur modifie seulement ses propres tickets_img

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = TicketForm(instance=ticket)

    return render(request, '../templates/modify_ticket/modify_ticket.html', {
        'form': form, 'ticket': ticket
    })


@login_required
def modify_critique(request, critique_id):
    profile = request.user.profile
    critique = get_object_or_404(Critique, id=critique_id, user=profile)
    ticket = get_object_or_404(Ticket, id=critique.ticket.id)

    if request.method == 'POST':
        form = CritiqueForm(request.POST, request.FILES, instance=critique)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = CritiqueForm(instance=critique)

    return render(request, '../templates/modify_critique/modify_critique.html', {
        'form': form,
        'critique': critique,
        'ticket': ticket
    })


@login_required
def create_critique(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = CritiqueForm(request.POST, request.FILES)
        if form.is_valid():
            critique_form = form.save(commit=False)
            critique_form.user_id = request.user.profile.id
            critique_form.ticket = ticket
            critique_form.save()
            messages.success(request, 'Votre Critique a été envoyé avec succès !')
            return redirect('create_critique', ticket_id=ticket.id)
    else:
        form = CritiqueForm()
    return render(request, '../templates/critique/critique.html', {
        'ticket': ticket,
        'critique_form': form
    })
