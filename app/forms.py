from django import forms
from .models import Ticket, Critique


class UserSearchForm(forms.Form):
    """
    Form for searching users by username.

    Attributes:
        -username (CharField): A text input for entering the username, with a placeholder.
    """
    username = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d\'utilisateur',
        })
    )


class TicketForm(forms.ModelForm):
    """
    Form for creating or updating a Ticket instance.

    Uses fields:
        -title: The title of the ticket.
        -description: A text description of the ticket.
        -image: An image associated.
    """
    class Meta:
        """ Metadata for the TicketForm, specifying the model and fields to include"""
        model = Ticket
        fields = ['title', 'description', 'image']


class CritiqueForm(forms.ModelForm):
    """Form for creating or updating a Critique instance, including a rating and Metadata."""
    NOTE_CHOICES = [(i, str(i)) for i in range(6)]  # Choice from 0 to 5

    note = forms.ChoiceField(
        choices=NOTE_CHOICES,
        widget=forms.RadioSelect()
    )

    class Meta:
        """Metadata for the CritiqueForm, specifying the model, labels and fields to include"""
        model = Critique
        fields = ['critique_title', 'note', 'commentaire']
        labels = {
            'critique_title': 'Title',
        }
