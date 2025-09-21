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
    path('historias/subir/', views.subir_historia, name='subir_historia'),
]
