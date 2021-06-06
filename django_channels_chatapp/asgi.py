"""
ASGI config for django_channels_chatapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


# Set this first to avoid any ORM issues with `AuthMiddlewareStack`.
default_asgi_application = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from core import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_channels_chatapp.settings')

application = ProtocolTypeRouter({
    'http': default_asgi_application,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})

