from django.conf import settings
from adopcion.models import Adoption
from usuarios.models import UserProfile

def user_adoption_notifications(request):
    """
    Context processor para notificaciones de adopciones pendientes para el responsable (dueño) de mascotas.
    Retorna 'notificaciones' con las solicitudes de adopción pendientes para el usuario autenticado.
    """
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            user_profile = (
                UserProfile.objects.select_related("user")
                .filter(user=request.user)
                .first()
            )
            notificaciones = (
                Adoption.objects.filter(
                    pet__creator=user_profile,
                )
                .only("adopterName", "pet", "created_at")
                .order_by("-created_at")
            )
        else:
            notificaciones = None
        return {"user_authenticated": True, "notificaciones": notificaciones}
    else:
        return {"user_authenticated": False, "notificaciones": None}
