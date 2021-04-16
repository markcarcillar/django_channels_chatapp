from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import SenderModel, ReceiverModel, ChatKeyModel

@receiver(post_save , sender=User)
def new_user(sender , instance , created , **kwargs):
    if created:
        # Create SenderModel and ReceiverModel for new User instance
        SenderModel.objects.create(user=instance)
        ReceiverModel.objects.create(user=instance)

        # Create a ChatKeyModel for each user on all users with the new user.
        # Even the new user itself will have its own ChatKeyModel
        users = User.objects.all()
        for user in users:
            user_username = user.get_username()
            new_user_username = instance.get_username()
            usernames = [user_username]
            if not user_username == new_user_username:
                # If not the user username is equal to the new instance username
                # add the username
                # This is to avoid two username 
                usernames.append(new_user_username)
            ChatKeyModel.objects.create(
                usernames=usernames
            )