import json
from asgiref.sync import sync_to_async

from django.contrib.auth.models import User

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import get_user

from .models import SenderModel, ReceiverModel, ChatModel, ChatKeyModel

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Setup the user1 and user2
        user1 = await get_user(self.scope)
        user2_pk = self.scope['url_route']['kwargs']['user2_pk']
        user2 = await self.get_usermodel(pk=user2_pk)

        # Checks if user1 is authenticated, if not reject the request.
        # user1 should be authenticated because it will be the one who 
        # will become the sender to chat
        if not user1.is_authenticated:
            await self.close()
        
        # Setup user1 and user2 username, and 
        # user1 sender and user2 receiver model
        self.user1_username = user1.get_username()
        self.user2_username = user2.get_username()
        self.user1_sender = await self.get_sendermodel(user=user1)
        self.user2_receiver = await self.get_receivermodel(user=user2)

        # Get the key from ChatKeyModel and create room name
        usernames = [self.user1_username]
        if not self.user1_username == self.user2_username:
            # We only add the user2 username to `usernames` list when 
            # it is not the same with user1 username because we don't 
            # want to duplicate it
            usernames.append(self.user2_username)
        chatkey = await database_sync_to_async(ChatKeyModel.get_by_usernames)(
            usernames
        )
        self.room_name = f'chat_room_{chatkey.key}'
        
        # Add the room name to channel layer
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Accept the request
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove the room name to channel layer
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        # Decode the message
        text_data_as_json = json.loads(text_data)
        message = text_data_as_json['message']

        # Setup message for ChatModel
        message = {
            'sender': self.user1_sender,
            'receiver': self.user2_receiver,
            'text': message
        }

        # Save the message to database
        await self.create_chatmodel(**message)

        # Get the created ChatModel, format the chat log,
        # then send it to the channel layer
        chatmodel = await self.get_latest_chatmodel(**message)
        log = f'{chatmodel.log.date()} - {str(chatmodel.log.time())[:8]}'
        chatmodel = {
            'sender_username': self.user1_username,
            'receiver_username': self.user2_username,
            'text': chatmodel.text,
            'log': log
        }
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'send.message',
                'chatmodel': chatmodel
            }
        )
    
    async def send_message(self, event):
        # Get the chatmodel from event then make it as json format
        message = json.dumps({'chatmodel': event['chatmodel']})

        # Send the message to websocket
        await self.send(
            text_data=message
        )

    @database_sync_to_async
    def get_usermodel(self, **kwargs):
        return User.objects.get(**kwargs)
    
    @database_sync_to_async
    def get_receivermodel(self, **kwargs):
        return ReceiverModel.objects.get(**kwargs)
    
    @database_sync_to_async
    def get_sendermodel(self, **kwargs):
        return SenderModel.objects.get(**kwargs)
    
    @database_sync_to_async
    def get_latest_chatmodel(self, **kwargs):
        return ChatModel.objects.filter(**kwargs).last()
    
    @database_sync_to_async
    def create_chatmodel(self, **kwargs):
        return ChatModel.objects.create(**kwargs)