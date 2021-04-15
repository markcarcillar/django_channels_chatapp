from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class SenderModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
    
class ReceiverModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class ChatModel(models.Model):
    sender = models.ForeignKey(SenderModel, on_delete=models.CASCADE)
    receiver = models.ForeignKey(ReceiverModel, on_delete=models.CASCADE)
    text = models.TextField()
    log = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.sender.user.username} chats {self.receiver.user.username}'