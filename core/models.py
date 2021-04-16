from uuid import uuid4
from secrets import token_hex

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class SenderModel(models.Model):
    '''Model for the sender of chat'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.get_username()
    
class ReceiverModel(models.Model):
    '''Model for the receiver of chat'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.get_username()

class ChatModel(models.Model):
    '''Model for chat'''
    sender = models.ForeignKey(SenderModel, on_delete=models.CASCADE)
    receiver = models.ForeignKey(ReceiverModel, on_delete=models.CASCADE)
    text = models.TextField()
    log = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.sender.user.get_username()} chats {self.receiver.user.get_username()}'
    
class ChatKeyModel(models.Model):
    '''Contains the chat key that will be used for group name on channel layer'''
    key = models.UUIDField(default=uuid4)
    usernames = models.JSONField(default=list)

    def __str__(self):
        text = 'Users: '
        for count, username in enumerate(self.usernames):
            text += username + ', '
        # Return without ', ' at last
        return text[:len(text) - 2]