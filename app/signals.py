from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Ticket
import os


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal receiver to create a Profile instance when a new User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Signal receiver to save the Profile instance when the User is saved"""
    instance.profile.save()


@receiver(post_delete, sender=Ticket)
def delete_ticket_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)