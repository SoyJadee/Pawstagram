# Endpoint para retornar todas las notificaciones mezcladas (AJAX)
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import Histories
from .models import Like
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, QuerySet
from mascota.models import Pet
from .models import Post, Comment, Notifications as Notification
from usuarios.models import UserProfile
from tienda.models import Store, Product
from salud.models import ServicesHealth
from adopcion.forms import AdoptionForm
from adopcion.models import Adoption
from django.contrib import messages
from supabase import create_client
from django.conf import settings
import os
import uuid
import re
import logging
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timesince import timesince
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.http import StreamingHttpResponse
import json, time


@login_required
def all_notifications_fragment(request):
    from adopcion.models import Adoption
    from mascota.models import Pet
    from usuarios.models import UserProfile
    from index.models import Notifications as Notification

    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    mascotas = []
    if user_profile:
        mascotas = list(Pet.objects.filter(creator=user_profile))
    # Traer notificaciones y agregar foto del post si existe
    notificaciones = list(
        Notification.objects.filter(user=request.user)
        .select_related("post")
        .values("id", "type", "message", "created_at", "is_read", "post_id")
    )
    post_ids = [n["post_id"] for n in notificaciones if n["post_id"]]
    post_photos = {p.id: p.photo_url for p in Post.objects.filter(id__in=post_ids)}
    for n in notificaciones:
        n["notif_type"] = n["type"]
        n["is_adoption"] = False
        n["photo_url"] = post_photos.get(n["post_id"])
    if mascotas:
        adopciones = list(
            Adoption.objects.filter(pet__in=mascotas).values(
                "id", "adopterName", "message", "created_at", "pet_id", "is_read"
            )
        )
        pet_map = {p.idPet: p.name for p in mascotas}
    else:
        adopciones = []
        pet_map = {}
    for a in adopciones:
        a["notif_type"] = "adoption"
        a["is_adoption"] = True
        a["pet_name"] = pet_map.get(a["pet_id"], "Mascota")
    all_notifs = notificaciones + adopciones
    all_notifs.sort(key=lambda x: x["created_at"], reverse=True)
    html = render_to_string(
        "all_notifications_fragment.html", {"all_notifs": all_notifs}
    )
    return JsonResponse({"html": html})


# Endpoint para retornar solo el fragmento de solicitudes de adopción (para AJAX)


@login_required
def adoption_notifications_fragment(request):
    from adopcion.models import Adoption
    from mascota.models import Pet
    from usuarios.models import UserProfile

    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    mascotas = Pet.objects.filter(creator=user_profile)
    notificaciones_adopciones = Adoption.objects.filter(pet__in=mascotas).order_by(
        "-created_at"
    )
    html = render_to_string(
        "adoption_notifications_fragment.html",
        {"notificaciones_adopciones": notificaciones_adopciones},
    )
    return HttpResponse(html)


# Endpoint para subir historias tipo Instagram


@login_required
@require_POST
def subir_historia(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "not_authenticated"})
    foto = request.FILES.get("foto_historia")
    if not foto:
        return JsonResponse({"success": False, "error": "no_file"})
    if foto.size > 10 * 1024 * 1024:
        return JsonResponse({"success": False, "error": "file_too_large"})
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if foto.content_type not in allowed_types:
        return JsonResponse({"success": False, "error": "invalid_type"})
    url = None
    upload_error = None
    if supabase:
        try:
            usuario = request.user.username
            nombre_archivo = f"{uuid.uuid4()}_{foto.name}"
            ruta_supabase = f"Usuarios/{usuario}/histories/{nombre_archivo}"
            foto_data = foto.read()
            foto.seek(0)
            res = supabase.storage.from_("Usuarios").upload(
                ruta_supabase, foto_data, {"content-type": foto.content_type}
            )
            # Si la respuesta indica error, lanzar excepción
            if hasattr(res, "error") and res.error:
                raise Exception(res.error)
            url_result = supabase.storage.from_("Usuarios").get_public_url(
                ruta_supabase
            )
            if isinstance(url_result, dict) and "publicUrl" in url_result:
                url = url_result["publicUrl"]
            else:
                url = url_result
            if url and url.endswith("?"):
                url = url[:-1]
        except Exception as e:
            logger.error(f"Error al subir historia a Supabase: {e}")
            upload_error = str(e)
    else:
        return JsonResponse({"success": False, "error": "storage_unavailable"})
    if not url:
        # Si no hay URL, pero no hubo error de subida, solo guardar la historia sin advertencia
        if upload_error:
            return JsonResponse(
                {"success": False, "error": upload_error or "upload_failed"}
            )
    historia = Histories.objects.create(author=request.user, photo_url=url or "")
    return JsonResponse({"success": True, "historia_id": historia.id, "photo_url": url})


# Endpoint AJAX para obtener notificaciones del usuario autenticado


@login_required
@require_GET
def notificaciones_json(request):
    notificaciones = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )[:30]
    data = []
    for n in notificaciones:
        # Si la notificación tiene post relacionado, obtener photo_url
        photo_url = None
        if hasattr(n, "post") and n.post and hasattr(n.post, "photo_url"):
            photo_url = n.post.photo_url
        data.append(
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": timesince(n.created_at) + " atrás",
                "photo_url": photo_url,
            }
        )
    return JsonResponse({"notificaciones": data}, encoder=DjangoJSONEncoder)


# Conteo rápido de notificaciones no leídas (para polling)
@login_required
@require_GET
def notificaciones_count(request):
    try:
        unread_app = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    except Exception:
        unread_app = 0
    try:
        # Adopciones no leídas de mis mascotas
        from mascota.models import Pet

        pets = Pet.objects.filter(creator__user=request.user)
        unread_adop = Adoption.objects.filter(pet__in=pets, is_read=False).count()
    except Exception:
        unread_adop = 0
    total_unread = int(unread_app) + int(unread_adop)
    return JsonResponse(
        {"unread": total_unread, "unread_app": unread_app, "unread_adop": unread_adop}
    )


# SSE: stream de notificaciones del usuario autenticado
@login_required
def notifications_stream(request):
    """
    Devuelve un stream SSE con eventos cuando haya nuevas notificaciones para el usuario.
    Estrategia simple con long-polling en memoria (proceso) sobre la base de datos.
    """
    # Headers SSE
    response = StreamingHttpResponse(content_type="text/event-stream; charset=utf-8")
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"  # Nginx: desactivar buffering

    user = request.user

    def gen():

        # Última marca temporal enviada para reducir queries
        last_ts = None
        # Primer envío: mandar un ping para abrir el canal
        yield f": ping\n\n"

        # Bucle de espera: 30 iteraciones x 2s = ~60s (luego el navegador reintenta)
        for _ in range(30):
            try:
                # Notificaciones del usuario
                notifs_qs = Notification.objects.filter(user=user)
                if last_ts:
                    notifs_qs = notifs_qs.filter(created_at__gt=last_ts)
                notifs = list(
                    notifs_qs.order_by("-created_at").values(
                        "id", "type", "message", "created_at", "is_read", "post_id"
                    )[:10]
                )

                # Adopciones para mascotas del usuario
                user_profile = (
                    UserProfile.objects.select_related("user").filter(user=user).first()
                )
                adopciones = []
                if user_profile:
                    mascotas = list(Pet.objects.filter(creator=user_profile))
                    if mascotas:
                        adop_qs = Adoption.objects.filter(pet__in=mascotas)
                        if last_ts:
                            adop_qs = adop_qs.filter(created_at__gt=last_ts)
                        adopciones = list(
                            adop_qs.order_by("-created_at").values(
                                "id",
                                "adopterName",
                                "message",
                                "created_at",
                                "pet_id",
                                "is_read",
                            )[:10]
                        )

                payload = {
                    "notifications": notifs,
                    "adoptions": adopciones,
                }

                # Si hay algo nuevo, enviar evento
                if notifs or adopciones:
                    # actualizar last_ts con el más reciente
                    newest_ts = None
                    for n in notifs:
                        ts = n.get("created_at")
                        if ts and (newest_ts is None or ts > newest_ts):
                            newest_ts = ts
                    for a in adopciones:
                        ts = a.get("created_at")
                        if ts and (newest_ts is None or ts > newest_ts):
                            newest_ts = ts
                    if newest_ts:
                        last_ts = newest_ts

                    data = json.dumps(payload, cls=DjangoJSONEncoder)
                    yield f"event: update\n"
                    yield f"data: {data}\n\n"
                else:
                    # Enviar ping periódico para mantener la conexión
                    yield f": ping\n\n"

                time.sleep(2)
            except Exception as e:
                # Logear y romper el stream de forma segura
                logger.error(f"SSE error: {e}")
                yield f"event: error\n"
                yield f"data: {json.dumps({'message': 'internal_error'})}\n\n"
                break

    response.streaming_content = gen()
    return response


# SSE de conteo de notificaciones no leídas
@login_required
def notifications_count_stream(request):
    response = StreamingHttpResponse(content_type="text/event-stream; charset=utf-8")
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"

    user = request.user

    def current_unread():
        try:
            unread_app = Notification.objects.filter(user=user, is_read=False).count()
        except Exception:
            unread_app = 0
        try:
            from mascota.models import Pet

            pets = Pet.objects.filter(creator__user=user)
            unread_adop = Adoption.objects.filter(pet__in=pets, is_read=False).count()
        except Exception:
            unread_adop = 0
        return int(unread_app) + int(unread_adop)

    def gen():
        last_val = None
        yield ": ping\n\n"
        for _ in range(60):  # ~120s si sleep=2
            try:
                v = current_unread()
                if v != last_val:
                    last_val = v
                    yield "event: count\n"
                    yield f"data: {json.dumps({'unread': v})}\n\n"
                else:
                    yield ": ping\n\n"
                time.sleep(2)
            except Exception as e:
                logger.error(f"SSE count error: {e}")
                yield "event: error\n"
                yield f"data: {json.dumps({'message': 'internal_error'})}\n\n"
                break

    response.streaming_content = gen()
    return response


# Marcar notificaciones como leídas


@require_POST
def marcar_notificaciones_leidas(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "not_authenticated"})
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    # Marcar adopciones como leídas
    from adopcion.models import Adoption
    from mascota.models import Pet
    from usuarios.models import UserProfile

    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    mascotas = Pet.objects.filter(creator=user_profile)
    Adoption.objects.filter(pet__in=mascotas, is_read=False).update(is_read=True)
    return JsonResponse({"success": True})


@require_POST
def like_post(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "not_authenticated"})
    post_id = request.POST.get("post_id")
    if not post_id:
        return JsonResponse({"success": False, "error": "no_post"})
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "not_found"})
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Crear notificación solo si el autor no es el mismo usuario
        if getattr(post, "author", None) and post.author.user != request.user:
            Notification.objects.create(
                post=post,
                user=post.author.user,
                referenceLike=like,
                type="like",
                message=f"{request.user.username} le dio like a tu post.",
                is_read=False,
            )
    likes_count = Like.objects.filter(post=post).count()
    return JsonResponse({"success": True, "liked": liked, "likes": likes_count})


# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar Supabase con manejo de errores
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None


def principal(request):
    # Eliminar comentarios con '{{' en el contenido (limpieza de datos)
    from .models import Comment

    # Limpieza de comentarios con '{{' (solo una vez, no en cada request en producción)
    if request.method == "GET":
        Comment.objects.filter(content__contains="{{").delete()
    mascotas = []
    if request.user.is_authenticated:
        try:
            from usuarios.models import UserProfile

            user_profile = UserProfile.objects.filter(user=request.user).first()
            if user_profile:
                mascotas = Pet.objects.filter(creator=user_profile)
            else:
                mascotas = []
        except Exception as e:
            logger.error(f"Error al obtener mascotas del usuario: {e}")
            messages.error(request, "Error al cargar tus mascotas.")

    form = AdoptionForm()
    adoption_success = False

    if request.method == "POST":
        # Publicar un post
        if request.user.is_authenticated and "mascota_id" in request.POST:
            try:
                rutaStorage = None
                mascota_id = request.POST.get("mascota_id")
                descripcion = request.POST.get("descripcion", "").strip()
                foto = request.FILES.get("foto")
                if not descripcion:
                    messages.error(request, "Debes escribir una descripción.")
                    return redirect("principal")
                if not foto:
                    messages.error(request, "Debes subir una foto.")
                    return redirect("principal")
                if foto.size > 5 * 1024 * 1024:
                    messages.error(
                        request, "La imagen es demasiado grande. Máximo 5MB."
                    )
                    return redirect("principal")
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                if foto.content_type not in allowed_types:
                    messages.error(
                        request, "Tipo de archivo no válido. Solo se permiten imágenes."
                    )
                    return redirect("principal")
                user_profile = getattr(request.user, "userprofile", None)
                if not user_profile:
                    messages.error(request, "Perfil de usuario no encontrado.")
                    return redirect("principal")
                mascota = Pet.objects.filter(
                    idPet=mascota_id, creator=user_profile
                ).first()
                if not mascota:
                    messages.error(
                        request, "Mascota no encontrada o no tienes permisos."
                    )
                    return redirect("principal")
                # Subir imagen a Supabase si está disponible
                url = None
                if supabase:
                    try:
                        usuario = request.user.username
                        nombre_mascota = mascota.name
                        nombre_archivo = f"{uuid.uuid4()}_{foto.name}"
                        ruta_supabase = f"{usuario}/{nombre_mascota}/{nombre_archivo}"
                        rutaStorage = ruta_supabase
                        logger.info(f"Subiendo imagen a Supabase: {ruta_supabase}")
                        foto_data = foto.read()
                        foto.seek(0)
                        res = supabase.storage.from_("Usuarios").upload(
                            ruta_supabase,
                            foto_data,
                            {"content-type": foto.content_type},
                        )
                        url_result = supabase.storage.from_("Usuarios").get_public_url(
                            ruta_supabase
                        )
                        if isinstance(url_result, dict) and "publicUrl" in url_result:
                            url = url_result["publicUrl"]
                        else:
                            url = url_result
                        if url and url.endswith("?"):
                            url = url[:-1]
                        logger.info(f"URL de imagen generada: {url}")
                    except Exception as e:
                        logger.error(f"Error al subir imagen a Supabase: {e}")
                        messages.error(
                            request, "Error al subir la imagen. Inténtalo de nuevo."
                        )
                        return redirect("principal")
                else:
                    messages.error(request, "Servicio de almacenamiento no disponible.")
                    return redirect("principal")
                post_obj = Post.objects.create(
                    pet=mascota,
                    author=user_profile,
                    content=descripcion,
                    photo_url=url,
                    photo_storage_path=rutaStorage,
                )
                messages.success(request, "¡Publicación realizada con éxito!")
                logger.info(f"Post creado exitosamente: {post_obj.id}")
            except Exception as e:
                logger.error(f"Error al crear el post: {e}")
                messages.error(
                    request, "Error al crear la publicación. Inténtalo de nuevo."
                )
            return redirect("principal")
        # Guardar comentario
        elif request.user.is_authenticated and "comment_post_id" in request.POST:
            comment_content = request.POST.get("comment_content", "").strip()
            # Validación de tipo y contra inyección SQL
            if not comment_content or len(comment_content) < 2:
                messages.error(
                    request, "El comentario no puede estar vacío o ser muy corto."
                )
                return redirect("principal")
            if len(comment_content) > 300:
                messages.error(
                    request, "El comentario es demasiado largo (máx. 300 caracteres)."
                )
                return redirect("principal")
            patrones_sql = [
                r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
                r"(['\";=])",
            ]
            for patron in patrones_sql:
                if re.search(patron, comment_content, re.IGNORECASE):
                    messages.error(
                        request,
                        "El comentario contiene caracteres o palabras no permitidas.",
                    )
                    return redirect("principal")
            comment_post_id = request.POST.get("comment_post_id")
            if comment_content and comment_post_id:
                try:
                    post = Post.objects.get(id=comment_post_id)
                    comment = Comment.objects.create(
                        post=post, user=request.user, content=comment_content
                    )
                    # Crear notificación solo si el autor no es el mismo usuario
                    if (
                        getattr(post, "author", None)
                        and post.author.user != request.user
                    ):
                        Notification.objects.create(
                            post=post,
                            user=post.author.user,
                            referenceComment=comment,
                            type="comment",
                            message=f"{request.user.username} comentó en tu post.",
                            is_read=False,
                        )
                    if request.headers.get("x-requested-with") == "XMLHttpRequest":
                        from django.http import JsonResponse

                        return JsonResponse(
                            {
                                "success": True,
                                "username": request.user.username,
                                "content": comment_content,
                            }
                        )
                    messages.success(request, "Comentario publicado.")
                except Exception as e:
                    logger.error(f"Error al guardar el comentario: {e}")
                    if request.headers.get("x-requested-with") == "XMLHttpRequest":
                        from django.http import JsonResponse

                        return JsonResponse({"success": False})
                    messages.error(request, "No se pudo guardar el comentario.")
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                from django.http import JsonResponse

                return JsonResponse({"success": False})
            return redirect("principal")

        form = AdoptionForm(request.POST)
        if form.is_valid():
            try:
                adoption = form.save(commit=False)
                adoption.is_read = False  # Siempre nueva solicitud no leída
                # obtener pet id enviado desde el modal (limpiar y manejar varios casos)
                pet_id = (
                    request.POST.get("pet_id") or request.POST.get("mascota_id") or ""
                ).strip()
                pet = None
                if pet_id:
                    # intentar por campo idPet (PK nombrado) primero
                    pet = Pet.objects.filter(idPet=pet_id).first()
                    if not pet:
                        # intentar por pk numérico por si se usa otra convención
                        try:
                            pet = Pet.objects.filter(pk=int(pet_id)).first()
                        except Exception:
                            pet = None
                if not pet:
                    logger.warning(
                        f"Solicitud de adopción  no corresponde a ninguna Mascota"
                    )
                    messages.error(
                        request,
                        "Mascota inválida. No se pudo procesar la solicitud de adopción.",
                    )
                else:
                    adoption.pet = pet
                    solicitudPasada = Adoption.objects.filter(
                        pet=pet, adopterEmail=adoption.adopterEmail
                    ).exists()
                    if solicitudPasada:
                        messages.warning(
                            request,
                            "Ya has enviado una solicitud de adopción para esta mascota.",
                        )
                    else:
                        adoption.save()
                        adoption_success = True
            except Exception as e:
                logger.error(f"Error al guardar adopción: {e}")
                messages.error(
                    request,
                    "Error al procesar la solicitud de adopción. Inténtalo de nuevo.",
                )
            # No redirigir, mostrar mensaje en modal
        else:
            messages.error(
                request,
                "Error en el formulario de adopción. Revisa los datos ingresados.",
            )

    # GET request or after POST handling, always render the page
    posts = (
        Post.objects.all()
        .order_by("-created_at")
        .prefetch_related("comments__user", "pet", "author")
    )
    # IDs de posts que el usuario ya ha dado like
    user_liked_post_ids = set()
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            Like.objects.filter(user=request.user).values_list("post_id", flat=True)
        )
    # Historias activas (últimas 24h)
    from django.utils import timezone

    desde = timezone.now() - timezone.timedelta(hours=24)
    historias_qs = (
        Histories.objects.filter(created_at__gte=desde)
        .select_related("author")
        .order_by("author", "created_at")
    )
    historias_por_usuario = {}
    for h in historias_qs:
        username = h.author.username
        if username not in historias_por_usuario:
            historias_por_usuario[username] = {"user": h.author, "historias": []}
        historias_por_usuario[username]["historias"].append(h)
    context = {
        "mascotas_usuario": mascotas,
        "form": form,
        "posts": posts,
        "adoption_success": adoption_success,
        "user_liked_post_ids": user_liked_post_ids,
        "historias_por_usuario": historias_por_usuario,
        "user_authenticated": request.user.is_authenticated,
        "usuario_actual": (
            request.user.username if request.user.is_authenticated else ""
        ),
    }
    return render(request, "Principal.html", context)


def search_with_rank(
    model: QuerySet,
    fields: list,
    query: str,
    config: str = "spanish",
    threshold: float = 0.06,
):
    """
    Realiza una búsqueda con rank en un modelo dado.

    :param model: QuerySet del modelo a buscar.
    :param fields: Lista de campos a incluir en el vector de búsqueda.
    :param query: Término de búsqueda.
    :param config: Configuración del idioma para la búsqueda.
    :param threshold: Umbral mínimo de relevancia para incluir resultados.
    :return: QuerySet con los resultados ordenados por relevancia.
    """
    search_vector = SearchVector(*fields, config=config)
    search_query = SearchQuery(query, search_type="websearch", config=config)
    return (
        model.annotate(rank=SearchRank(search_vector, search_query))
        .filter(rank__gte=threshold)
        .order_by("-rank")
    )


def search(request):
    querysearch = request.GET.get("search", "").strip()

    context = {
        "mascots": [],
        "stores": [],
        "services": [],
        "products": [],
        "query": querysearch,
    }

    # Retornar vacío si no hay término
    if not querysearch:
        return render(request, "results.html", context)

    # Validaciones básicas
    if len(querysearch) > 50:
        messages.error(request, "El término de búsqueda es demasiado largo.")
        return render(request, "results.html", context)
    if not re.match(r"^[a-zA-Z0-9\s]*$", querysearch):
        messages.error(
            request, "La búsqueda solo puede contener letras, números y espacios."
        )
        return render(request, "results.html", context)
    if len(querysearch) < 3:
        messages.warning(request, "Ingresa al menos 3 caracteres para buscar.")
        return render(request, "results.html", context)

    # Búsquedas con rank (evalúan al iterar)
    # tipoAnimal es FK: usar el campo relacionado 'nombre' para el vector
    mascotas_qs = search_with_rank(
        Pet.objects, ["name", "tipoAnimal__nombre", "breed"], querysearch
    )
    servicios_qs = search_with_rank(
        ServicesHealth.objects, ["name", "type", "services", "owner"], querysearch
    )
    tiendas_qs = search_with_rank(Store.objects, ["name"], querysearch)
    # Fix: faltaba la coma entre "name" y "description"
    productos_qs = search_with_rank(
        Product.objects, ["name", "description"], querysearch
    )

    # Materializar en listas (evita reevaluaciones)
    # Paginación individual por tipo (param: page_j, page_e, page_c, page_a)
    def paginate(qs, param, per_page=10):
        paginator = Paginator(qs, per_page)
        page = request.GET.get(param, 1)
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    mascotas_page = paginate(mascotas_qs, "page_m")
    servicios_page = paginate(servicios_qs, "page_s")
    tiendas_page = paginate(tiendas_qs, "page_t")
    productos_page = paginate(productos_qs, "page_p")

    mascotas = list(mascotas_page.object_list)
    servicios = list(servicios_page.object_list)
    tiendas = list(tiendas_page.object_list)
    productos = list(productos_page.object_list)

    # Contadores para filtros
    mascotas_count = mascotas_qs.count()
    servicios_count = servicios_qs.count()
    tiendas_count = tiendas_qs.count()
    productos_count = productos_qs.count()
    total_count = mascotas_count + servicios_count + tiendas_count + productos_count

    context.update(
        {
            "query": querysearch,
            "mascotas": mascotas,
            "servicios": servicios,
            "tiendas": tiendas,
            "productos": productos,
            "mascotas_page": mascotas_page,
            "servicios_page": servicios_page,
            "tiendas_page": tiendas_page,
            "productos_page": productos_page,
            "mascotas_count": mascotas_count,
            "servicios_count": servicios_count,
            "tiendas_count": tiendas_count,
            "productos_count": productos_count,
            "total_count": total_count,
        }
    )

    # Renderizar plantilla correcta
    return render(request, "resultados.html", context)
