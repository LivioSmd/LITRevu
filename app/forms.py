from fileinput import FileInput

from django import forms
from django.forms import ImageField

from .models import Ticket, Critique


class UserSearchForm(forms.Form):
    username = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d\'utilisateur',
        })
    )


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']



class CritiqueForm(forms.ModelForm):
    NOTE_CHOICES = [(i, str(i)) for i in range(6)]  # Choix de 0 à 5

    note = forms.ChoiceField(
        choices=NOTE_CHOICES,
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Critique
        fields = ['critique_title', 'note', 'commentaire']
        labels = {
            'critique_title': 'Title',
        }
