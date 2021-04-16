from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.shortcuts import render
from django.contrib.auth.models import User

from .models import SenderModel, ReceiverModel, ChatModel

class HomeView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        context = {
            'users': User.objects.all().exclude(
                        username=request.user.get_username()
                    )
        }
        return render(request, 'core/home.html', context)

class ChatView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, receiver_pk, *args, **kwargs):
        # Setup sender and receiver models
        user1_sender = SenderModel.objects.get(pk=request.user.pk)
        user2_sender = SenderModel.objects.get(pk=receiver_pk)
        user1_receiver = ReceiverModel.objects.get(pk=request.user.pk)
        user2_receiver = ReceiverModel.objects.get(pk=receiver_pk)

        # Get the sender and receiver chats to each other
        user1_chats = ChatModel.objects.filter(sender=user1_sender, receiver=user2_receiver)
        user2_chats = ChatModel.objects.filter(sender=user2_sender, receiver=user1_receiver)

        # Put the chats in to `chats` list and sort it with its pk using
        # the `sort()` and `self.sort_pk()` method
        chats = [chat1 for chat1 in user1_chats]
        chats.extend([chat2 for chat2 in user2_chats])
        chats.sort(key=self.sort_pk)

        # Add the chats and user2_receiver to context
        # for passing to template
        context = {
            'chats': chats,
            'user2_receiver': user2_receiver
        }
        return render(request, 'core/chat.html', context)
    
    def sort_pk(self, model):
        '''Returns `model.pk`. Can be use for sorting a queryset of Django Model'''
        return model.pk