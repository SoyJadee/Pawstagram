
from django.urls import path
from . import views

urlpatterns = [
	path('', views.servicios_salud, name='servicios_salud'),
	path('obtener-comentarios-salud/', views.obtener_comentarios_salud, name='obtener_comentarios_salud'),
	path('guardar-comentario-salud/', views.guardar_comentario_salud, name='guardar_comentario_salud'),
    path('ruta-direcciones/', views.obtener_ruta_openrouteservice, name='ruta-direcciones'),
]
