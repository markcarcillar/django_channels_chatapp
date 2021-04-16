from django.contrib import admin

from .models import SenderModel, ReceiverModel, ChatModel

models = [SenderModel, ReceiverModel, ChatModel]

for model in models:
    admin.site.register(model)