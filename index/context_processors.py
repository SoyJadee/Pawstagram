from django.conf import settings
from adopcion.models import Adoption
from usuarios.models import UserProfile
def user_authenticated(request):
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            user_profile = UserProfile.objects.select_related('user').filter(user=request.user).first()
            notificaciones = Adoption.objects.filter(responsable=user_profile, status='pending').only('adopterName', 'pet','created_at').order_by('-created_at')
        else:
            notificaciones = None
        return {
            'user_authenticated': True,
            'notificaciones': notificaciones
        }
    else:
        return {
            'user_authenticated': False,
            'notificaciones': None
        }
