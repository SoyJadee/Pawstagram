from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from index.models import Post, Comment, Like, Notifications
from mascota.models import Pet
from adopcion.models import Adoption
from .forms import UserCreationForm, LoginForm, DeleteUserForm, EditProfileForm
from index.views import like_post
from index.forms import PostForm
from mascota.forms import PetForm
from adopcion.forms import AdoptionForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_smart_ratelimit import rate_limit
from common.security import sanitize_string
import re
import logging
import uuid
from django.http import JsonResponse
from supabase import create_client
from django.conf import settings

allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
logger = logging.getLogger(__name__)

try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None

@rate_limit(key='ip', rate='5/m',)
def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return redirect("/admin/")
        else:
            return redirect("perfil")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            email_exists = User.objects.filter(
                email=form.cleaned_data["email"]
            ).exists()
            username_exists = User.objects.filter(
                username=form.cleaned_data["username"]
            ).exists()
            phone_exists = UserProfile.objects.filter(
                phone=form.cleaned_data["phone"]
            ).exists()
            if email_exists:
                messages.error(request, "Correo Electrónico ya registrado")
            elif username_exists:
                messages.error(
                    request, "Elija otro nombre de usuario, este ya está en uso"
                )
            else:
                try:
                    with transaction.atomic():
                        user = form.save(commit=True)
                        UserProfile.objects.create(
                            user=user,
                            phone=form.cleaned_data.get("phone"),
                            is_foundation=form.cleaned_data.get("is_foundation"),
                        )
                    messages.success(
                        request,
                        "Usuario registrado correctamente. Ahora puedes iniciar sesión.",
                    )
                    return redirect("login")
                except IntegrityError:
                    messages.error(
                        request,
                        "No se pudo crear el cliente (teléfono o cédula ya existe).",
                    )
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = UserCreationForm()

    return render(request, "Registro.html", {"form": form})

@rate_limit(key='ip', rate='5/m',)
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return redirect("/admin/")
        else:
            return redirect("perfil")

    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        username_input = request.POST.get("username", "").strip()
        username_input = sanitize_string(username_input)
        if "@" in username_input:
            try:
                related_user = User.objects.get(email__iexact=username_input)
                data = request.POST.copy()
                data["username"] = related_user.username
                form = LoginForm(request, data=data)
            except User.DoesNotExist:
                pass

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            messages.success(request, "Has iniciado sesión correctamente.")
            if request.user.is_staff and request.user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect("principal")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "login.html", {"form": form})


INJECTION_PATTERNS = [
    r"[;\\'\"\\\\]|(--|#|/\\*|\\*/|xp_)",
    r"(<|>|script|alert|onerror|onload)",
]


def is_injection_attempt(value):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def petAdopted(request):
    user = UserProfile.objects.select_related("user").filter(user=request.user).first()
    if not user:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")
    return Pet.objects.filter(creator=user, status="adopted").count()


def petAvailable(request):
    user = UserProfile.objects.select_related("user").filter(user=request.user).first()
    if not user:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")
    return Pet.objects.filter(creator=user, status="available").count()

@login_required
@rate_limit(key='user', rate='5/m',)
def perfil_view(request):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")
    return render(
        request,
        "perfil.html",
        {
            "usuario": user_profile,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
        },
    )

@login_required
@rate_limit(key='user', rate='5/m',)
def editProfileView(request):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")
    else:
        form = EditProfileForm(instance=user_profile, user=request.user)
    return render(
        request,
        "editProfile.html",
        {
            "usuario": user_profile,
            "form": form,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
        },
    )

@login_required
@rate_limit(key='user', rate='5/m',)
def configuracion_view(request):
    def is_injection_attempt(value):
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    if request.method == "POST":
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if is_injection_attempt(email):
                messages.error(request, "El email contiene caracteres no permitidos.")
                return redirect("delete_account")
            elif request.user.email != email:
                messages.error(request, "El email no coincide con el de la cuenta.")
                return redirect("configuracion")
            else:
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
                return redirect("principal")
    else:
        form = DeleteUserForm()
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    return render(
        request,
        "configuracion.html",
        {
            "form": form,
            "usuario": user_profile,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
        },
    )

@login_required
@rate_limit(key='user', rate='5/m',)
def petsUserView(request):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")

    form = None
    open_edit = False
    url = None

    if request.method == "GET":
        pet_id = request.GET.get("editar", "").strip()
        pet_id = sanitize_string(pet_id)
        if pet_id:
            instance = Pet.objects.filter(idPet=pet_id, creator=user_profile).first()
            if instance:
                form = PetForm(instance=instance)
                open_edit = True
            else:
                form = PetForm()
        else:
            form = PetForm()

    elif request.method == "POST":
        pet_id = request.POST.get("pet_id", "").strip()
        pet_id = sanitize_string(pet_id)
        if pet_id:
            instance = Pet.objects.filter(idPet=pet_id, creator=user_profile).first()
            if not instance:
                messages.error(request, "Mascota no encontrada.")
                return redirect("pets_user")
            form = PetForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                edited_pet = form.save(commit=False)
                image = form.cleaned_data.get("profile_photo_url")
                # Solo si se subió una nueva imagen
                if image and hasattr(image, "size"):
                    if image.size > 5 * 1024 * 1024:
                        form.add_error(
                            "profile_photo_url",
                            "El tamaño de la imagen no debe exceder 5MB.",
                        )
                    elif (
                        hasattr(image, "content_type")
                        and image.content_type not in allowed_types
                    ):
                        form.add_error(
                            "profile_photo_url",
                            "Tipo de imagen no permitido. Usa JPEG, PNG, GIF o WEBP.",
                        )
                    elif supabase:
                        try:
                            # Eliminar imagen previa si existe
                            if instance.profile_photo_storage_path:
                                bucket_name = "Usuarios"
                                ruta = instance.profile_photo_storage_path
                                directorio = "/".join(ruta.split("/")[:-1])
                                nombre_archivo = ruta.split("/")[-1]
                                archivos = supabase.storage.from_(bucket_name).list(
                                    path=directorio
                                )
                                if any(
                                    archivo["name"] == nombre_archivo
                                    for archivo in archivos
                                ):
                                    supabase.storage.from_(bucket_name).remove([ruta])
                            usuario_name = request.user.username
                            image_name = f"{uuid.uuid4()}_{image.name}"
                            ruta_supabase = (
                                f"{usuario_name}/{edited_pet.name}/profile/{image_name}"
                            )
                            edited_pet.profile_photo_storage_path = ruta_supabase
                            image_data = image.read()
                            image.seek(0)
                            supabase.storage.from_("Usuarios").upload(
                                ruta_supabase,
                                image_data,
                                {"content-type": image.content_type},
                            )
                            url_result = supabase.storage.from_(
                                "Usuarios"
                            ).get_public_url(ruta_supabase)
                            url = (
                                url_result["publicURL"]
                                if isinstance(url_result, dict)
                                and "publicURL" in url_result
                                else url_result
                            )
                            if url and url.endswith("?"):
                                url = url[:-1]
                            edited_pet.profile_photo_url = url
                        except Exception as e:
                            form.add_error(
                                "profile_photo_url",
                                "Error al subir la imagen. Intenta nuevamente.",
                            )
                    else:
                        form.add_error(
                            "profile_photo_url",
                            "Servicio de almacenamiento no disponible. Contacta al administrador.",
                        )
                if not form.errors:
                    edited_pet.save()
                    messages.success(request, "Mascota actualizada correctamente.")
                    return redirect("pets_user")
            # Si hay errores, se mostrarán en el formulario
            open_edit = True
        else:
            form = PetForm(request.POST, request.FILES)
            if form.is_valid():
                new_pet = form.save(commit=False)
                new_pet.creator = user_profile
                image = form.cleaned_data.get("profile_photo_url")
                if not image:
                    form.add_error("profile_photo_url", "Por favor sube una imagen.")
                elif image.size > 5 * 1024 * 1024:
                    form.add_error(
                        "profile_photo_url",
                        "El tamaño de la imagen no debe exceder 5MB.",
                    )
                elif (
                    hasattr(image, "content_type")
                    and image.content_type not in allowed_types
                ):
                    form.add_error(
                        "profile_photo_url",
                        "Tipo de imagen no permitido. Usa JPEG, PNG, GIF o WEBP.",
                    )
                elif supabase:
                    try:
                        usuario_name = request.user.username
                        image_name = f"{uuid.uuid4()}_{image.name}"
                        ruta_supabase = (
                            f"{usuario_name}/{new_pet.name}/profile/{image_name}"
                        )
                        new_pet.profile_photo_storage_path = ruta_supabase
                        image_data = image.read()
                        image.seek(0)
                        supabase.storage.from_("Usuarios").upload(
                            ruta_supabase,
                            image_data,
                            {"content-type": image.content_type},
                        )
                        url_result = supabase.storage.from_("Usuarios").get_public_url(
                            ruta_supabase
                        )
                        url = (
                            url_result["publicURL"]
                            if isinstance(url_result, dict)
                            and "publicURL" in url_result
                            else url_result
                        )
                        if url and url.endswith("?"):
                            url = url[:-1]
                        new_pet.profile_photo_url = url
                    except Exception as e:
                        form.add_error(
                            "profile_photo_url",
                            "Error al subir la imagen. Intenta nuevamente.",
                        )
                else:
                    form.add_error(
                        "profile_photo_url",
                        "Error de configuración del servidor. Contacta al administrador.",
                    )
                if not form.errors:
                    new_pet.save()
                    messages.success(request, "Mascota guardada correctamente.")
                    return redirect("pets_user")
            # Si hay errores, se mostrarán en el formulario

    return render(
        request,
        "mascotasUser.html",
        {
            "usuario": user_profile,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
            "pets": Pet.objects.filter(creator=user_profile)
            .order_by("created_at")
            .all(),
            "form": form,
            "open_edit": open_edit,
        },
    )

@login_required
@rate_limit(key='user', rate='5/m',)
def publicacionesUserView(request):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")

    posts = Post.objects.filter(author=user_profile).order_by("created_at").all()
    print("posts:", posts)
    return render(
        request,
        "publicaciones.html",
        {
            "usuario": user_profile,
            "posts": posts,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
        },
    )
@rate_limit(key='ip', rate='5/m',)
def postView(request, post_id):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")

    post = get_object_or_404(Post, id=post_id)

    adoption_success = False
    form = AdoptionForm(
        initial={
            "adopterEmail": request.user.email,
            "adopterName": request.user.first_name + " " + request.user.last_name,
            "adopterPhone": user_profile.phone,
        }
    )

    if request.method == "POST":
        if (
            request.POST.get("comment_content") is not None
            and request.headers.get("x-requested-with") == "XMLHttpRequest"
        ):
            comment_content = request.POST.get("comment_content", "").strip()
            comment_content = sanitize_string(comment_content)
            if not comment_content:
                return JsonResponse({"success": False})
            try:
                comment = Comment.objects.create(
                    post=post, user=request.user, content=comment_content
                )
                # Notificar al autor si es distinto al usuario actual
                if post.author and post.author.user != request.user:
                    Notifications.objects.create(
                        post=post,
                        user=post.author.user,
                        referenceComment=comment,
                        type="comment",
                        message=f"{request.user.username} comentó en tu post.",
                        is_read=False,
                    )
                return JsonResponse(
                    {
                        "success": True,
                        "username": request.user.username,
                        "content": comment_content,
                    }
                )
            except Exception as e:
                logger.exception(f"Error al guardar el comentario: {e}")
                return JsonResponse({"success": False})

        # Comentario por submit normal (no AJAX)
        if request.POST.get("comment_content") is not None:
            comment_content = request.POST.get("comment_content", "").strip()
            comment_content = sanitize_string(comment_content)
            if not comment_content or len(comment_content) < 2:
                messages.error(
                    request, "El comentario no puede estar vacío o ser muy corto."
                )
                return redirect("post_view", post_id=post.id)
            if len(comment_content) > 300:
                messages.error(
                    request, "El comentario es demasiado largo (máx. 300 caracteres)."
                )
                return redirect("post_view", post_id=post.id)
            if comment_content and not is_injection_attempt(comment_content):
                try:
                    comment = Comment.objects.create(
                        post=post, user=request.user, content=comment_content
                    )
                    if post.author and post.author.user != request.user:
                        Notifications.objects.create(
                            post=post,
                            user=post.author.user,
                            referenceComment=comment,
                            type="comment",
                            message=f"{request.user.username} comentó en tu post.",
                            is_read=False,
                        )
                    messages.success(request, "Comentario publicado.")
                except Exception as e:
                    logger.exception(f"Error al guardar el comentario (no AJAX): {e}")
                    messages.error(request, "No se pudo guardar el comentario.")
            return redirect("post_view", post_id=post.id)

        # Proceso de adopción
        form = AdoptionForm(request.POST)
        if form.is_valid():
            try:
                adoption = form.save(commit=False)
                pet = post.pet
                if pet:
                    pet = (
                        Pet.objects.filter(idPet=pet.idPet).first()
                        or Pet.objects.filter(pk=pet.idPet).first()
                    )
                if not pet:
                    logger.warning(f"Solicitud de adopción: inválido")
                    messages.error(
                        request,
                        "Mascota inválida. No se pudo procesar la solicitud de adopción.",
                    )
                else:
                    solicitudPasada = Adoption.objects.filter(
                        adopterEmail=adoption.adopterEmail, pet=pet
                    )
                    if solicitudPasada.exists():
                        messages.error(
                            request,
                            "Ya has enviado una solicitud de adopción para esta mascota.",
                        )
                        return redirect("post_view", post_id=post_id)
                    else:
                        adoption.pet = pet
                        adoption.save()
                        adoption_success = True
                    messages.success(request, "Solicitud de adopción enviada.")
            except Exception as e:
                logger.exception(f"Error al guardar adopción: {e}")
                messages.error(
                    request,
                    "Error al procesar la solicitud de adopción. Inténtalo de nuevo.",
                )
        else:
            messages.error(
                request,
                "Error en el formulario de adopción. Revisa los datos ingresados.",
            )

    # Estado de like del usuario actual
    liked = Like.objects.filter(post=post, user=request.user).exists()
    user_liked_post_ids = [post.id] if liked else []

    return render(
        request,
        "post.html",
        {
            "form": form,
            "usuario": user_profile,
            "post": post,
            "adoptados": petAdopted(request),
            "disponibles": petAvailable(request),
            "user_authenticated": request.user.is_authenticated,
            "user_liked_post_ids": user_liked_post_ids,
            "adoption_success": adoption_success,
        },
    )

@login_required
@rate_limit(key='user', rate='5/m',)
def deletePostView(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        messages.error(request, "Publicación no encontrada.")
        return redirect("posts_user")
    if post.author.user != request.user:
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect("posts_user")
    try:
        # Eliminar imagen de Supabase si existe
        if post.photo_storage_path and supabase:
            try:
                logger.info(
                    f"Intentando eliminar la imagen de Supabase: {post.photo_storage_path}"
                )
                bucket_name = "Usuarios"
                ruta = post.photo_storage_path

                # Extraer el directorio y el nombre del archivo
                directorio = "/".join(ruta.split("/")[:-1])
                nombre_archivo = ruta.split("/")[-1]

                # Verificar si el archivo existe en Supabase
                archivos = supabase.storage.from_(bucket_name).list(path=directorio)

                if any(archivo["name"] == nombre_archivo for archivo in archivos):
                    resultado_eliminacion = supabase.storage.from_(bucket_name).remove(
                        [ruta]
                    )
            except Exception as e:
                logger.exception(f"Error al eliminar la imagen de Supabase: {e}")
        post.delete()
        messages.success(request, "Publicación eliminada correctamente.")
    except Exception as e:
        logger.exception(f"Error al eliminar la publicación: {e}")
        messages.error(request, "Error al eliminar la publicación. Inténtalo de nuevo.")
    return redirect("posts_user")

@login_required
@rate_limit(key='user', rate='5/m',)
def editPostView(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        messages.error(request, "Publicación no encontrada.")
        return redirect("posts_user")
    if post.author.user != request.user:
        messages.error(request, "No tienes permiso para editar esta publicación.")
        return redirect("posts_user")

    if request.method == "POST":
        try:
            user_profile = (
                UserProfile.objects.select_related("user")
                .filter(user=request.user)
                .first()
            )
            instance = Post.objects.filter(id=post_id, author=user_profile).first()
            if not instance:
                messages.error(request, "Publicación no encontrada.")
                return redirect("posts_user")

            form = PostForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                edited_post = form.save(commit=False)
                image = form.cleaned_data.get("image")

                # Si se subió una nueva imagen, validar y subir a Supabase
                if image and hasattr(image, "size"):
                    if image.size > 5 * 1024 * 1024:
                        form.add_error(
                            "image", "El tamaño de la imagen no debe exceder 5MB."
                        )
                    elif (
                        hasattr(image, "content_type")
                        and image.content_type not in allowed_types
                    ):
                        form.add_error(
                            "image",
                            "Tipo de imagen no permitido. Usa JPEG, PNG, GIF o WEBP.",
                        )
                    elif supabase:
                        try:
                            # Eliminar imagen previa si existe
                            if edited_post.photo_storage_path:
                                bucket_name = "Usuarios"
                                ruta = edited_post.photo_storage_path
                                directorio = "/".join(ruta.split("/")[:-1])
                                nombre_archivo = ruta.split("/")[-1]
                                archivos = supabase.storage.from_(bucket_name).list(
                                    path=directorio
                                )
                                if any(
                                    archivo.get("name") == nombre_archivo
                                    for archivo in archivos
                                ):
                                    supabase.storage.from_(bucket_name).remove([ruta])
                            # Subir nueva imagen
                            usuario_name = request.user.username
                            image_name = f"{uuid.uuid4()}_{image.name}"
                            ruta_supabase = (
                                f"{usuario_name}/{edited_post.pet.name}/{image_name}"
                            )
                            edited_post.photo_storage_path = ruta_supabase

                            image_data = image.read()
                            image.seek(0)
                            supabase.storage.from_("Usuarios").upload(
                                ruta_supabase,
                                image_data,
                                {"content-type": image.content_type},
                            )
                            url_result = supabase.storage.from_(
                                "Usuarios"
                            ).get_public_url(ruta_supabase)
                            url = (
                                url_result.get("publicURL")
                                if isinstance(url_result, dict)
                                else url_result
                            )
                            if url and isinstance(url, str) and url.endswith("?"):
                                url = url[:-1]
                            edited_post.photo_url = url
                        except Exception as e:
                            logger.exception(f"Error al subir imagen del post: {e}")
                            form.add_error(
                                "image", "Error al subir la imagen. Intenta nuevamente."
                            )
                    else:
                        form.add_error(
                            "image",
                            "Servicio de almacenamiento no disponible. Contacta al administrador.",
                        )

                if not form.errors:
                    edited_post.save()
                    messages.success(request, "Publicación actualizada correctamente.")
                    return redirect("posts_user")
        except Exception as e:
            logger.exception(f"Error al editar la publicación: {e}")
            messages.error(
                request, "Error al editar la publicación. Inténtalo de nuevo."
            )
    else:
        form = PostForm(instance=post)
    return render(request, "editPost.html", {"form": form, "post": post})
