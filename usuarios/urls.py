from django.urls import path, include
from . import views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
    LogoutView,
)
from decouple import config

urlpatterns = [
    path("iniciar_sesion/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", LogoutView.as_view(template_name="logout.html"), name="logout"),
    path(
        "change_password/",
        PasswordResetView.as_view(
            template_name="change_password.html",
            from_email=config('EMAIL_HOST_USER'),
            html_email_template_name="password_reset_email.html",
        ),
        name="change_password",
    ),
    path(
        "reset_password_sent/",
        PasswordResetDoneView.as_view(template_name="password_reset_sent.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="password_reset_form.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),
        name="password_reset_complete",
    ),
    path("perfil/", views.perfil_view, name="perfil"),
    path("editar_perfil/", views.editProfileView, name="editar_perfil"),
    path("configuracion/", views.configuracion_view, name="configuracion"),
    path("mascotas/", views.petsUserView, name="pets_user"),
    path("publicaciones/", views.publicacionesUserView, name="posts_user"),
    path("publicacion/<int:post_id>/", views.postView, name="post_view"),
    path("editar_post/<int:post_id>/", views.editPostView, name="editar_post"),
    path("eliminar_post/<int:post_id>/", views.deletePostView, name="eliminar_post"),
]
