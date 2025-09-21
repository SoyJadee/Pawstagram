from django.urls import path
from . import views

urlpatterns = [
	path('', views.tienda, name='tienda'),
	path('catalogo/', views.catalogo, name='catalogo'),
]
