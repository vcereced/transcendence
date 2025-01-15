import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from game_app import routing  # Importamos las rutas de WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # Usamos el middleware para autenticación de WebSockets
        URLRouter(
            routing.websocket_urlpatterns  # Aquí se definirán nuestras rutas WebSocket
        )
    ),
})
