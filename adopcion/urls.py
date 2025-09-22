from django.urls import path
from . import views

urlpatterns = [
    path('solicitudes_adopcion/', views.solicitudes_adopcion, name='solicitudes_adopcion'),
]