"""
URL configuration for internethub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include  # Ensure 'include' is explicitly imported here
from rest_framework.routers import DefaultRouter
from core import views as core_views  # Or tv.views if moved

router = DefaultRouter()
router.register(r'api/videos', core_views.VideoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # 'include' is used here
    path('', include('core.urls')),     # 'include' is used here too
    path('tv/', include('tv.urls')),  # Add this for tv.internethub.co
    path('', include(router.urls)),  # API at /api/videos/
    path('games/spircre/', include('games.spircre.urls', namespace='spircre')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)