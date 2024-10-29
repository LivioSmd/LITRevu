from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import PositiveSmallIntegerField
import os


class Profile(models.Model):
    """
    Model representing a user profile.

    Attributes:
        -user (OneToOneField)
        -subscriptions (ManyToManyField)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscriptions = models.ManyToManyField(User, related_name='subscribers', blank=True)

    def __str__(self):
        """Returns a string representation of the profile, showing the user's username."""
        return f'{self.user.username}'

    def get_subscriptions(self):
        """Returns the list of users this user is following"""
        return self.subscriptions.all()

    def get_subscribers(self):
        """Returns a list of users following this user"""
        return self.user.subscribers.all()


class Ticket(models.Model):
    """
    Model representing a support or review ticket created by a user.

    Attributes:
        -title (CharField)
        -description (TextField)
        -user (ForeignKey)
        -image (ImageField)
        -time_created (DateTimeField)
    """
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    # models.CASCADE: profile is delete, ticket too
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='static/tickets_img')
    time_created = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.image:
            # Delete file system image
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        """Returns the title of the ticket as its string representation."""
        return self.title


class Critique(models.Model):
    """
    Model representing a critique or review for a specific ticket.

    Attributes:
        -critique_title (CharField)
        -ticket (ForeignKey)
        -note (PositiveSmallIntegerField)
        -user (ForeignKey)
        -commentaire (TextField)
        -time_created (DateTimeField)
    """
    critique_title = models.CharField(max_length=2048)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    note = PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    commentaire = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns the title of the critique as its string representation."""
        return self.critique_title
