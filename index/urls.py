from django.urls import path
from . import views

urlpatterns = [
    path('notificaciones/adopciones/fragment/',
         views.adoption_notifications_fragment, name='adoption_notifications_fragment'),
    path('notificaciones/all/fragment/', views.all_notifications_fragment,
         name='all_notifications_fragment'),
    path('', views.principal, name='principal'),
    path('like/', views.like_post, name='like_post'),
    path('search/', views.search, name='search'),
    path('notificaciones/leidas/', views.marcar_notificaciones_leidas,
         name='marcar_notificaciones_leidas'),
    path('notificaciones/json/', views.notificaciones_json,
         name='notificaciones_json'),
    path('notificaciones/count/', views.notificaciones_count,
         name='notificaciones_count'),
    path('notificaciones/count/stream/', views.notifications_count_stream,
         name='notifications_count_stream'),
     # Stream Server-Sent Events (SSE) como proxy backend seguro
     path('notificaciones/stream/', views.notifications_stream, name='notifications_stream'),
    path('historias/subir/', views.subir_historia, name='subir_historia'),
]
