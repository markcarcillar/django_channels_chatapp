from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.shortcuts import render
from django.contrib.auth.models import User

from .models import SenderModel, ReceiverModel, ChatModel

class HomeView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Add all the users to context even the current authenticated user
        context = {
            'users': User.objects.all()
        }
        return render(request, 'core/home.html', context)

class ChatView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, user2_pk, *args, **kwargs):
        # Setup the user1 and user2
        user1 = User.objects.get(pk=request.user.pk)
        user2 = User.objects.get(pk=user2_pk)

        # Setup sender and receiver models
        user1_sender = SenderModel.objects.get(pk=user1.sendermodel.pk)
        user2_sender = SenderModel.objects.get(pk=user2.sendermodel.pk)
        user1_receiver = ReceiverModel.objects.get(pk=user1.receivermodel.pk)
        user2_receiver = ReceiverModel.objects.get(pk=user2.receivermodel.pk)

        # Get the sender and receiver chats to each other
        user1_chats = ChatModel.objects.filter(sender=user1_sender, receiver=user2_receiver)
        user2_chats = ChatModel.objects.filter(sender=user2_sender, receiver=user1_receiver)

        # Put the chats in to `chats` list
        chats = [chat1 for chat1 in user1_chats]
        if not user1.get_username() == user2.get_username():
            # If the user1 and user2 are not the same, 
            # add the user2_chats and sort the `chats` 
            # with its pk using the `sort()` and 
            # `self.sort_pk()` method
            chats.extend([chat2 for chat2 in user2_chats])
            chats.sort(key=self.sort_pk)

        # Add the chats and user2 to context
        # for passing to template
        context = {
            'chats': chats,
            'user2': user2
        }
        return render(request, 'core/chat.html', context)
    
    def sort_pk(self, model):
        '''Returns `model.pk`. Can be use for sorting a queryset of Django Model'''
        return model.pk