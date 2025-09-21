from django.shortcuts import render, redirect
from .models import UserProfile
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from index.models import Post
from mascota.models import Pet
from .forms import UserCreationForm, LoginForm, DeleteUserForm, EditProfileForm
from mascota.forms import PetForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import re, logging, uuid
from supabase import create_client
from django.conf import settings

allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
logger = logging.getLogger(__name__)

try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    logger.error(f"Error al inicializar Supabase: {e}")
    supabase = None


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return redirect("/admin/")
        else:
            return redirect("perfil")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
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


INJECTION_PATTERNS = [
    r"[;\\'\"\\\\]|(--|#|/\\*|\\*/|xp_)",
    r"(<|>|script|alert|onerror|onload)",
]


@login_required
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
                return redirect("delete_account")
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
def petsUserView(request):
    user_profile = (
        UserProfile.objects.select_related("user").filter(user=request.user).first()
    )
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect("login")

    form = None
    open_edit = False

    if request.method == "GET":
        pet_id = request.GET.get("editar", "").strip()
        if pet_id:
            instance = Pet.objects.filter(idPet=pet_id, creator=user_profile).first()
            form = PetForm(instance=instance)
            open_edit = True if instance else False
        else:
            form = PetForm()

    elif request.method == "POST":
        pet_id = request.POST.get("pet_id", "").strip()
        if pet_id:
            instance = Pet.objects.filter(idPet=pet_id, creator=user_profile).first()
            if not instance:
                messages.error(request, "Mascota no encontrada.")
                return redirect("pets_user")
            form = PetForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                edited_pet = form.save(commit=False)
                image = form.cleaned_data.get("profile_photo_url")
                if image != instance.profile_photo_url:
                    if image:
                        if image.size > 5 * 1024 * 1024:
                            messages.error(
                                request, "El tamaño de la imagen no debe exceder 5MB."
                            )
                            return redirect("pets_user")
                        if (
                            hasattr(image, "content_type")
                            and image.content_type not in allowed_types
                        ):
                            messages.error(
                                request,
                                "Tipo de imagen no permitido. Usa JPEG, PNG, GIF o WEBP.",
                            )
                            return redirect("pets_user")
                        if supabase:
                            try:
                                # Verificar si hay una imagen previa y eliminarla de Supabase
                                if instance.profile_photo_storage_path and supabase:
                                    try:
                                        logger.info(
                                            f"Intentando eliminar la imagen previa de Supabase: {instance.profile_photo_storage_path}"
                                        )
                                        bucket_name = "Usuarios"
                                        ruta = instance.profile_photo_storage_path

                                        # Extraer el directorio y el nombre del archivo
                                        directorio = "/".join(ruta.split("/")[:-1])
                                        nombre_archivo = ruta.split("/")[-1]

                                        # Verificar si el archivo existe en Supabase
                                        archivos = supabase.storage.from_(
                                            bucket_name
                                        ).list(path=directorio)

                                        if any(
                                            archivo["name"] == nombre_archivo
                                            for archivo in archivos
                                        ):
                                            resultado_eliminacion = (
                                                supabase.storage.from_(
                                                    bucket_name
                                                ).remove([ruta])
                                            )
                                    except Exception as e:
                                        return redirect("pets_user")
                                usuario_name = request.user.username
                                image_name = f"{uuid.uuid4()}_{image.name}"
                                ruta_supabase = f"{usuario_name}/{edited_pet.name}/profile/{image_name}"
                                edited_pet.profile_photo_storage_path = ruta_supabase

                                image_data = image.read()
                                image.seek(0)
                                _ = supabase.storage.from_("Usuarios").upload(
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

                                messages.error(
                                    request,
                                    "Error al subir la imagen. Intenta nuevamente.",
                                )
                                return redirect("pets_user")
                        else:
                            messages.error(
                                request,
                                "Servicio de almacenamiento no disponible. Contacta al administrador.",
                            )
                            return redirect("pets_user")
                edited_pet.save()
                messages.success(request, "Mascota actualizada correctamente.")
                return redirect("pets_user")
        else:
            form = PetForm(request.POST, request.FILES)
            if form.is_valid():
                new_pet = form.save(commit=False)
                new_pet.creator = user_profile

                image = form.cleaned_data.get("profile_photo_url")

                if not image:
                    messages.error(request, "Por favor sube una imagen.")
                    return redirect("pets_user")
                if image.size > 5 * 1024 * 1024:
                    messages.error(
                        request, "El tamaño de la imagen no debe exceder 5MB."
                    )
                    return redirect("pets_user")
                if (
                    hasattr(image, "content_type")
                    and image.content_type not in allowed_types
                ):
                    messages.error(
                        request,
                        "Tipo de imagen no permitido. Usa JPEG, PNG, GIF o WEBP.",
                    )
                    return redirect("pets_user")

                if supabase:
                    try:
                        usuario_name = request.user.username
                        image_name = f"{uuid.uuid4()}_{image.name}"
                        ruta_supabase = (
                            f"{usuario_name}/{new_pet.name}/profile/{image_name}"
                        )
                        new_pet.profile_photo_storage_path = ruta_supabase
                        logger.info(f"Subiendo imagen a Supabase en {ruta_supabase}")
                        image_data = image.read()
                        image.seek(0)
                        _ = supabase.storage.from_("Usuarios").upload(
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
                        logger.info(f"Imagen subida exitosamente. URL: {url}")
                    except Exception as e:
                        logger.exception(f"Error al subir la imagen a Supabase: {e}")
                        messages.error(
                            request, "Error al subir la imagen. Intenta nuevamente."
                        )
                        return redirect("pets_user")
                else:
                    messages.error(
                        request,
                        "Error de configuración del servidor. Contacta al administrador.",
                    )
                    return redirect("pets_user")

                new_pet.profile_photo_url = url
                new_pet.save()
                messages.success(request, "Mascota guardada correctamente.")
                return redirect("pets_user")
            else:
                messages.error(
                    request,
                    "Hay errores en el formulario. Revisa los campos resaltados.",
                )
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