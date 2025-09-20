from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView

urlpatterns = [
    path('iniciar_sesion/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', PasswordChangeView.as_view(
        template_name='change_password.html', success_url='/'), name='change_password'),
    path('reset_password_sent/', PasswordResetDoneView.as_view(
        template_name='password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password_reset_form.html',
         success_url='iniciar_sesion/reset_password_complete/'), name='password_reset_confirm'),
    path('reset_password_complete/', PasswordResetCompleteView.as_view(
        template_name='password_reset_done.html'), name='password_reset_complete'),
    path('perfil/', views.perfil_view, name='perfil'),
]
