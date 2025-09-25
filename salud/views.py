import logging
import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServicesHealth, Reviews, Service, Specialty
from .forms import ReviewForm
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django_smart_ratelimit import rate_limit
from common.security import sanitize_string
import re

logger = logging.getLogger(__name__)

# Centralized rate limits with safe fallbacks
RL = getattr(settings, 'RATE_LIMITS', {})
RL_ORS_IP = RL.get('ors_ip', '60/m')
RL_SALUD_IP = RL.get('salud_ip', '120/m')

patrones_sql = [
    r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
    r"(['\";=])",
]
def contiene_sql_injection(texto):
    for patron in patrones_sql:
        if re.search(patron, texto, re.IGNORECASE):
            return True
    return False

@csrf_protect
@rate_limit(key='ip', rate=RL_ORS_IP)
def obtener_ruta_openrouteservice(request):
    if request.method == "POST":
        import json

        data = json.loads(request.body.decode("utf-8"))
        origen = data.get("origen")  # [lon, lat]
        destino = data.get("destino")  # [lon, lat]
        if not origen or not destino:
            return JsonResponse({"error": "Faltan coordenadas"}, status=400)
        api_key = getattr(settings, 'OPENROUTESERVICE_API_KEY', '')
        if not api_key:
            return JsonResponse({"error": "Servicio no disponible"}, status=503)
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        body = {"coordinates": [origen, destino]}
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        }
        try:
            response = requests.post(
                url, json=body, headers=headers, timeout=10)
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse(
                    {
                        "error": "Error en OpenRouteService",
                        "status": response.status_code,
                    },
                    status=500,
                )
        except Exception as e:
            logger.exception(f"Error solicitando ruta")
            return JsonResponse({"error": "internal_error"}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)


def obtener_comentarios_salud(request):
    service_id = request.GET.get("service_id")
    service_id = sanitize_string(service_id)
    comentarios = []
    if not service_id:
        return JsonResponse({"success": False, "error": "Falta service_id"}, status=400)
    # Validar que sea un entero para evitar 500 por conversión
    try:
        service_id_int = int(service_id)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "service_id inválido"}, status=400)

    reviews = Reviews.objects.filter(
        service_id=service_id_int).order_by("-created_at")
    for r in reviews:
        comentarios.append(
            {
                "rating": float(r.rating),
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
            }
        )
    return JsonResponse({"success": True, "comentarios": comentarios})


@rate_limit(key='ip', rate=RL_SALUD_IP)
def servicios_salud(request):
    if request.method == "GET":
        servicios = ServicesHealth.objects.all()
        veterinarias = []

        now = datetime.now().time()
        for s in servicios:
            coords = None
            if s.latitude is not None and s.longitude is not None:
                coords = {"lat": s.latitude, "lon": s.longitude}
            estado = "cerrado"
            if s.horarioStart and s.horarioEnd:
                if s.horarioStart <= now <= s.horarioEnd:
                    estado = "abierto"
            # Obtener servicios y especialidades relacionados
            services_list = list(s.services.all().values_list('name', flat=True))
            specialties_list = list(s.specialties.all().values_list('name', flat=True))
            veterinarias.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "coords": coords,
                    "type": s.type,
                    "email": s.email,
                    "services": services_list,
                    "specialties": specialties_list,
                    "description": s.description,
                    "consultprice": s.consultPrice,
                    "estado": estado,
                    "phone": s.phone,
                }
            )
        return render(request, "salud.html", {"veterinarias": veterinarias, "form": ReviewForm(initial={
            "email": request.user.email if request.user.is_authenticated else ""})})

    elif request.method == "POST":
        form = ReviewForm(request.POST)
        rating = request.POST.get("rating")
        rating = sanitize_string(rating)
        service_id = request.POST.get("servicio")
        service_id = sanitize_string(service_id)

        if contiene_sql_injection(service_id) and contiene_sql_injection(rating) and contiene_sql_injection(request.POST.get("email")) and contiene_sql_injection(request.POST.get("comment")):
            messages.error(
                request,
                "Los datos ingresados contienen caracteres o palabras no permitidas.",
            )
            return redirect("servicios_salud")
        

        # Validaciones básicas fuera del form (rating/servicio vienen de inputs ocultos)
        if not rating or not service_id:
            messages.error(
                request, "Faltan campos obligatorios (calificación o servicio).")
            return redirect("servicios_salud")

        try:
            rating_val = int(rating)
            if rating_val < 1 or rating_val > 5:
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, "La calificación es inválida.")
            return redirect("servicios_salud")

        try:
            initial_service = ServicesHealth.objects.get(id=service_id)
        except ServicesHealth.DoesNotExist:
            messages.error(request, "El servicio seleccionado no existe.")
            return redirect("servicios_salud")

        if not form.is_valid():
            # Mostrar errores del formulario en mensajes y redirigir (PRG)
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
            return redirect("servicios_salud")

        # Evitar duplicados por email + servicio
        registroPasado = Reviews.objects.filter(
            email=form.cleaned_data.get("email"), service_id=service_id
        ).exists()
        if registroPasado:
            messages.warning(
                request, "Ya has enviado una reseña para este servicio.")
            return redirect("servicios_salud")

        try:
            Reviews.objects.create(
                email=form.cleaned_data.get("email"),
                comment=sanitize_string(form.cleaned_data.get("comment")),
                rating=rating_val,
                service=initial_service,
                created_at=timezone.now(),
            )
            messages.success(request, "¡Gracias por tu reseña!")
        except Exception as e:
            logger.exception(f"Error guardando reseña: {e}")
            messages.error(
                request, "No se pudo guardar tu reseña por un error interno.")
        return redirect("servicios_salud")
