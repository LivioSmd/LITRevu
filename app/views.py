from itertools import chain
from django.db.models import CharField, Value

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import UserSearchForm, TicketForm, CritiqueForm
from .models import Ticket, Critique, Profile


def login_user(request):
    """
    Method for user login.
    Redirects to 'flux' if authenticated

    Args:
        request (HttpRequest): The request object.

    Else returns:
        Redirects to 'login' or renders the 'login'.
    """
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
    """
    Method for user logout.

    Args:
        request (HttpRequest): The request object.

    Redirects to 'login'
    """
    logout(request)
    return redirect('login')


def register(request):
    """
    Handle user registration.

    Redirects to 'flux' if authenticated.

    Args:
        request (HttpRequest): The request object.

    Else Returns:
        Redirects to 'flux' or renders the registration page.
    """
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
    """
    Display the activity feed for the logged-in user.

    Retrieves tickets and critiques from followed users and the logged-in user,
    Combines and sorts all entries by creation time.

    Args:
        request (HttpRequest): The request object.

    Returns:
        Renders the activity feed template with the combined posts.
    """
    profile = request.user.profile

    followed_users = profile.subscriptions.all()  # Retrieve users followed of logged-in user
    # Retrieve profiles followed of logged-in user
    # .exclude(id=profile.id) avoids duplicates if the user follows him/herself
    followed_profiles = Profile.objects.filter(user__in=followed_users).exclude(id=profile.id)
    followed_users_tickets = Ticket.objects.filter(user__in=followed_profiles)  # Retrieve tickets from followed
    followed_users_critique = Critique.objects.filter(user__in=followed_profiles)  # Retrieve critiques from followed

    # tickets & critiques from logged-in user
    my_tickets = Ticket.objects.filter(user=profile)
    my_critiques = Critique.objects.filter(user=profile)

    # critiques in response to the logged-in user's posts, not including his/her own reviews
    critiques_on_my_tickets = Critique.objects.filter(ticket__user=profile).exclude(user=profile)

    # Annotate each queryset to distinguish between tickets and critiques
    followed_users_tickets = followed_users_tickets.annotate(content_type=Value('TICKET', CharField()))
    my_tickets = my_tickets.annotate(content_type=Value('TICKET', CharField()))
    followed_users_critique = followed_users_critique.annotate(content_type=Value('CRITIQUE', CharField()))
    my_critiques = my_critiques.annotate(content_type=Value('CRITIQUE', CharField()))
    critiques_on_my_tickets = critiques_on_my_tickets.annotate(content_type=Value('CRITIQUE', CharField()))

    # Combine and sort posts and reviews
    posts = sorted(
        chain(followed_users_tickets, followed_users_critique,
              my_tickets, my_critiques, critiques_on_my_tickets),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, '../templates/flux/flux.html', context={'posts': posts})


@login_required
def subscription(request):
    """
    Manage user subscriptions and search for users.

    Allows the logged-in user to search for other users to subscribe to or unsubscribe from.

    Args:
        request (HttpRequest): The request object.

    Returns:
        Renders the subscription template with the search form and results.
    """
    search_users = None
    profile = request.user.profile

    # Check for GET parameters, because the GET method is automatically used when the page is generated.
    if request.method == 'GET' and request.GET:
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
                profile.subscriptions.remove(user_to_subscribe)  # unsubscribe
            else:
                profile.subscriptions.add(user_to_subscribe)  # Subscription
    return render(request, '../templates/subscription/subscription.html',
                  {'form_search': form_search, 'search_users': search_users, 'user_profile': profile})


@login_required
def create_ticket(request):
    """
    Handle ticket creation.

    On POST, validates and saves a new ticket associated with the logged-in user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        Renders the ticket creation template.
    """
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)  # Not yet saved in database
            ticket.user_id = request.user.profile.id  # Retrieves the profile ID of the current user
            ticket.save()  # Now save the ticket
            messages.success(request, 'Votre ticket a été envoyé avec succès !')  # Success message
            return redirect('create_ticket')
    else:
        form = TicketForm()
    return render(request, '../templates/ticket/ticket.html', {'form': form})


@login_required
def create_ticket_critique(request):
    """
    Handle ticket and critique creation.

    On POST, validates and saves both a new ticket and its associated critique for the logged-in user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        Renders the ticket and critique creation template.
    """
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
    """
    Display and manage the logged-in user's posts.

    Handles deletion of tickets and critiques submitted by the user.
    Retrieves the user's tickets and critiques after any deletions.

    Args:
        request (HttpRequest): The request object.

    Returns:
        Renders the user's posts template.
    """
    profile = request.user.profile

    if request.method == 'POST':
        ticket_id = request.POST.get('delete_ticket_id')  # Retrieves ticket id via form field
        critique_id = request.POST.get('delete_critique_id')
        if ticket_id:
            ticket_to_delete = get_object_or_404(Ticket, id=ticket_id, user=profile)  # Recovers ticket in db
            ticket_to_delete.delete()  # Delete ticket in db
        if critique_id:
            critique_to_delete = get_object_or_404(Critique, id=critique_id, user=profile)
            critique_to_delete.delete()  # Delete critique in db
    # Recover tickets and reviews after deletion
    my_tickets = Ticket.objects.filter(user=profile)
    my_critiques = Critique.objects.filter(user=profile)
    return render(request, '../templates/my_posts/my_posts.html', {
        'my_tickets': my_tickets,
        'my_critiques': my_critiques,
    })


@login_required
def modify_ticket(request, ticket_id):
    """
    Modify an existing ticket.

    Retrieves the ticket for the logged-in user and allows editing its details.

    Args:
        request (HttpRequest): The request object.
        ticket_id: The ID of the ticket to modify.

    Returns:
        Renders the ticket modification template.
    """
    profile = request.user.profile
    ticket = get_object_or_404(Ticket, id=ticket_id, user=profile)

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
    """
    Modify an existing critique.

    Retrieves the critique for the logged-in user and allows editing its details.

    Args:
        request (HttpRequest): The request object.
        critique_id: The ID of the critique to modify.

    Returns:
        Renders the critique modification template.
    """
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
    """
    Create a critique for a specified ticket.

    On POST, saves the critique associated with the ticket if the form is valid.

    Args:
        request (HttpRequest): The request object.
        ticket_id: The ID of the ticket for which the critique is created.

    Returns:
        Renders the critique creation template.
    """
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
