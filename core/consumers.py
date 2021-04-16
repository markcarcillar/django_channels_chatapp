from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import get_user

from .models import SenderModel, ReceiverModel, ChatModel

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Checks if user is authenticated, if not reject the request
        user = await get_user(self.scope)
        if not user.is_authenticated:
            self.close()
        
        # Get the SenderModel and ReceiverModel
        receiver_pk = self.scope['url_route']['kwargs']['receiver_pk']
        self.receivermodel = await self.get_receivermodel(receiver_pk)
        self.sendermodel = await self.get_sendermodel(user.sender.pk)

        # Create group name for room
        self.group_name = f'chat_{self.sendermodel.pk}_{receiver_pk}'
        
        # Add the `self.group_name` to channel layer
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the request
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    

    
    @database_sync_to_async
    def get_receivermodel(self, pk):
        return ReceiverModel.objects.get(pk=pk)
    
    @database_sync_to_async
    def get_sendermodel(self, pk):
        return SenderModel.objects.get(pk=pk)