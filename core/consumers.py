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
        
        # Setup sender and receiver models
        self.user1_sender = await self.get_sendermodel(user=user1)
        self.user2_sender = await self.get_sendermodel(user=user2)
        self.user1_receiver = await self.get_receivermodel(user=user1)
        self.user2_receiver = await self.get_receivermodel(user=user2)
       
        # Get the ChatKeyModel and create room name
        chatkey = await self.get_chatkeymodel(
                            user1_sender=self.user1_sender,
                            user2_sender=self.user2_sender,
                            user1_receiver=self.user1_receiver,
                            user2_receiver=self.user2_receiver
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

        # Save the message to database
        await self.create_chatmodel(
            sender=self.user1_sender,
            receiver=self.user2_receiver,
            text=message
        )

        # Send the message to channel layer
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'send_message',
                'message': message
            }
        )
    
    async def send_message(self, event):
        # Get the message from event then make it as json format
        message = json.dumps({'message': event['message']})

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
    def get_chatkeymodel(self, **kwargs):
        return ChatKeyModel.objects.get(**kwargs)
    
    @database_sync_to_async
    def create_chatmodel(self, **kwargs):
        return ChatModel.objects.create(**kwargs)