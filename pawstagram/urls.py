"""
URL configuration for pawstagram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import Http404
from index import views as index_views


def _raise_404(request, *args, **kwargs):
    raise Http404()


_clean_admin_url = (settings.ADMIN_URL or '').strip('/') + '/'

urlpatterns = [
    # Make /admin return our custom 404 page (even in DEBUG)
    path('admin', index_views.custom_404, name='admin_404_no_slash'),
    path('admin/', index_views.custom_404, name='admin_404'),
    # Mount real admin under secret path from settings.ADMIN_URL
    path(_clean_admin_url, admin.site.urls),
    path('', include('index.urls')),
    path('mascota/', include('mascota.urls')),
    path('usuario/', include('usuarios.urls')),
    path('adopcion/', include('adopcion.urls')),
    path('tienda/', include('tienda.urls')),
    path('salud/', include('salud.urls')),
]

# Global 404 handler so unmatched routes use our template in production
handler404 = 'index.views.custom_404'
