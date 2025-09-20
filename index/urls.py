from django.urls import path

from . import views

urlpatterns = [
    path('', views.principal, name='principal'),
    path('like/', views.like_post, name='like_post'),
    path('search/', views.search, name='search'),
]
