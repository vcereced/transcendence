import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game.settings')

django_asgi_app = get_asgi_application()

from game_app import routing  # Importamos las rutas de WebSocket
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(  # Usamos el middleware para autenticación de WebSockets
        URLRouter(
            routing.websocket_urlpatterns  # Aquí se definirán nuestras rutas WebSocket
        )
    ),
})
