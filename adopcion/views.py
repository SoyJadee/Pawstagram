from django.shortcuts import render
from .models import Adoption
from mascota.models import Pet
from django.contrib.auth.decorators import login_required
from django.db.models import Count


# Create your views here.
@login_required
def solicitudes_adopcion(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            # Filtrar solo mascotas del usuario que tengan al menos una solicitud
            pets = (
                Pet.objects.filter(creator__user=request.user)
                .annotate(adoption_count=Count("adoptions"))
                .filter(adoption_count__gt=0)
                .prefetch_related("adoptions")
            )

            pets_with_solicitudes = [
                {"pet": pet, "solicitudes": list(pet.adoptions.all())} for pet in pets
            ]
        except Exception:
            pets_with_solicitudes = []
            # Puedes agregar un mensaje en plantilla si quieres
        return render(
            request,
            "solicitudes_adopcion.html",
            {
                "pets_with_solicitudes": pets_with_solicitudes,
                "user": request.user,
                "db_error": len(pets_with_solicitudes) == 0,
            },
        )
    else:
        return render(request, "403.html")
