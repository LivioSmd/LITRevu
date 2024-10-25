from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import PositiveSmallIntegerField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscriptions = models.ManyToManyField(User, related_name='subscribers', blank=True)

    def __str__(self):
        return f'{self.user.username}'

    def get_subscriptions(self):
        """Retourne la liste des utilisateurs que cet utilisateur suit"""
        return self.subscriptions.all()

    def get_subscribers(self):
        """Retourne la liste des utilisateurs qui suivent cet utilisateur"""
        return self.user.subscribers.all()


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='static/tickets_img')
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Critique(models.Model):
    critique_title = models.CharField(max_length=2048)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    note = PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    commentaire = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.critique_title
