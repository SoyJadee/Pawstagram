from django.urls import path
from . import views

urlpatterns = [
	path('', views.tienda, name='tienda'),
	path('catalogo/<int:store_id>/', views.catalogo, name='catalogo'),
]
