from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import SenderModel, ReceiverModel

@receiver(post_save , sender=User)
def create_sender_receiver(sender , instance , created , **kwargs):
    if created:
        SenderModel.objects.create(user=instance)
        ReceiverModel.objects.create(user=instance)