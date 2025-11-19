import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the settings module explicitly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internethub.settings')

# Initialize Django ASGI application (this loads the app registry)
django_asgi_app = get_asgi_application()

# Import routing only after apps are loaded
import core.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})