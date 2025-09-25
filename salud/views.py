import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ServicesHealth, Reviews
from .forms import ReviewForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.utils import timezone
from django.contrib import messages

# Lightweight rate limiter using Django cache (per-IP, per-view)
def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')

def rate_limit(limit=10, period=60):
    """Allow at most `limit` requests per `period` seconds per client IP.
    Returns 429 with Retry-After when exceeded.
    """
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            ip = _client_ip(request)
            key = f"rl:{view_func.__name__}:{ip}"
            # Initialize counter with TTL if not present, else increment
            added = cache.add(key, 1, timeout=period)
            if not added:
                try:
                    current = cache.get(key, 0)
                    if current >= limit:
                        resp = JsonResponse({"error": "Demasiadas solicitudes"}, status=429)
                        resp["Retry-After"] = str(period)
                        return resp
                    cache.incr(key)
                except Exception:
                    # Fallback if backend doesn't support incr
                    current = cache.get(key, 0)
                    if current >= limit:
                        resp = JsonResponse({"error": "Demasiadas solicitudes"}, status=429)
                        resp["Retry-After"] = str(period)
                        return resp
                    cache.set(key, current + 1, timeout=period)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
@csrf_protect
@rate_limit(limit=10, period=60)
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
            # Service temporarily unavailable due to missing configuration.
            return JsonResponse({"error": "Servicio no disponible"}, status=503)
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        body = {"coordinates": [origen, destino]}
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
        }
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
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
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def obtener_comentarios_salud(request):
    service_id = request.GET.get("service_id")
    comentarios = []
    if not service_id:
        return JsonResponse({"success": False, "error": "Falta service_id"}, status=400)
    # Validar que sea un entero para evitar 500 por conversión
    try:
        service_id_int = int(service_id)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "service_id inválido"}, status=400)

    reviews = Reviews.objects.filter(service_id=service_id_int).order_by("-created_at")
    for r in reviews:
        comentarios.append(
            {
                "rating": float(r.rating),
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
            }
        )
    return JsonResponse({"success": True, "comentarios": comentarios})

def servicios_salud(request):
    if request.method == "GET":
        servicios = ServicesHealth.objects.all()
        veterinarias = []

        now = datetime.now().time()
        for s in servicios:
            # Usar latitude y longitude si existen
            coords = None
            if s.latitude is not None and s.longitude is not None:
                coords = {"lat": s.latitude, "lon": s.longitude}
            # Determinar estado abierto/cerrado
            estado = "cerrado"
            if s.horarioStart and s.horarioEnd:
                if s.horarioStart <= now <= s.horarioEnd:
                    estado = "abierto"
            veterinarias.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address,
                    "coords": coords,
                    "type": s.type,
                    "email": s.email,
                    "services": s.services,
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
        service_id = request.POST.get("servicio")

        # Validaciones básicas fuera del form (rating/servicio vienen de inputs ocultos)
        if not rating or not service_id:
            messages.error(request, "Faltan campos obligatorios (calificación o servicio).")
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
            messages.warning(request, "Ya has enviado una reseña para este servicio.")
            return redirect("servicios_salud")

        try:
            Reviews.objects.create(
                email=form.cleaned_data.get("email"),
                comment=form.cleaned_data.get("comment"),
                rating=rating_val,
                service=initial_service,
                created_at=timezone.now(),
            )
            messages.success(request, "¡Gracias por tu reseña!")
        except Exception as e:
            messages.error(request, f"No se pudo guardar tu reseña: {str(e)}")
        return redirect("servicios_salud")
