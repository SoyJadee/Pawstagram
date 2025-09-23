from django.conf import settings
from adopcion.models import Adoption
from usuarios.models import UserProfile
from index.models import Post, Notifications as Notification
from mascota.models import Pet


def user_authenticated(request):
    countPosts = Post.objects.count()
    countPets = Pet.objects.count()
    countUsers = UserProfile.objects.filter(
        user__is_active=True, user__is_staff=False, user__is_superuser=False
    ).count()
    notificaciones = []
    notif_unread = 0
    notif_unread_adopciones = 0
    notificaciones_adopciones = None
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                # Notificaciones de la tabla Notifications (index_notifications)
                notificaciones = Notification.objects.filter(
                    user=request.user
                ).order_by("-created_at")
                notif_unread = notificaciones.filter(is_read=False).count()
            except Exception:
                notificaciones = []
                notif_unread = 0
            # Notificaciones de adopciones para el responsable (todas las solicitudes asociadas a sus mascotas)
            try:
                user_profile = (
                    UserProfile.objects.select_related("user")
                    .filter(user=request.user)
                    .first()
                )
                mascotas = Pet.objects.filter(creator=user_profile)
                notificaciones_adopciones = (
                    Adoption.objects.filter(pet__in=mascotas)
                    .only("adopterName", "pet", "created_at", "is_read")
                    .order_by("-created_at")
                )
                notif_unread_adopciones = notificaciones_adopciones.filter(
                    is_read=False
                ).count()
            except Exception:
                mascotas = Pet.objects.none()
                notificaciones_adopciones = None
                notif_unread_adopciones = 0
        else:
            mascotas = Pet.objects.none()
            notificaciones = []
            notif_unread = 0
            notificaciones_adopciones = None
            notif_unread_adopciones = 0
        return {
            "user_authenticated": True,
            "notificaciones": notificaciones,
            "notif_unread": notif_unread + notif_unread_adopciones,
            "notificaciones_adopciones": notificaciones_adopciones,
            "mascotas_usuario": mascotas,
            "countPosts": countPosts,
            "countPets": countPets,
            "countUsers": countUsers,
        }
    else:
        return {
            "user_authenticated": False,
            "notificaciones": None,
            "notif_unread": 0,
            "notificaciones_adopciones": None,
            "mascotas_usuario": [],
            "countPosts": countPosts,
            "countPets": countPets,
            "countUsers": countUsers,
        }
