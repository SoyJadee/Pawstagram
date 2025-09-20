from django.conf import settings
from adopcion.models import Adoption
from usuarios.models import UserProfile
from index.models import Post, Notifications as Notification
from mascota.models import Pet


def user_authenticated(request):
    countPosts = Post.objects.count()
    countPets = Pet.objects.count()
    countUsers = UserProfile.objects.filter(
        user__is_active=True, user__is_staff=False, user__is_superuser=False).count()
    notificaciones = []
    notif_unread = 0
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                # Notificaciones de la tabla Notifications (index_notifications)
                notificaciones = Notification.objects.filter(
                    user=request.user).order_by('-created_at')
                notif_unread = notificaciones.filter(is_read=False).count()
            except Exception:
                notificaciones = []
                notif_unread = 0
        else:
            notificaciones = []
            notif_unread = 0
        return {
            'user_authenticated': True,
            'notificaciones': notificaciones,
            'notif_unread': notif_unread,
            'countPosts': countPosts,
            'countPets': countPets,
            'countUsers': countUsers,
        }
    else:
        return {
            'user_authenticated': False,
            'notificaciones': None,
            'notif_unread': 0,
            'countPosts': countPosts,
            'countPets': countPets,
            'countUsers': countUsers,
        }
