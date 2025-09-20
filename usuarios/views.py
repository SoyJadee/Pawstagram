from django.shortcuts import render, redirect
from .models import UserProfile
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from adopcion.models import Adoption
from .forms import UserCreationForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def custom_logout(request):
    logout(request)
    return render(request, 'logout.html')


# Create your views here.


def userAuthenticated(request):
    return request.user.is_authenticated


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            # Redirigir a la página de Django admin si es admin
            return redirect('/admin/')
        else:
            # Redirigir a la página principal u otra página adecuada
            return redirect('perfil')
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
                    request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
                return redirect("login")
            except IntegrityError:
                messages.error(
                    request, "No se pudo crear el cliente (teléfono o cédula ya existe).")
        else:
            messages.error(
                request, "Por favor corrige los errores en el formulario.")
    else:
        form = UserCreationForm()

    return render(request, "Registro.html", {"form": form})


def login_view(request):
    """Vista de login segura.
    """

    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            # Redirigir a la página de Django admin si es admin
            return redirect('/admin/')
        else:
            # Redirigir a la página principal u otra página adecuada
            return redirect('perfil')

    form = LoginForm()

    if request.method == 'POST':
        print("Intento de login")
        # Enlazar el formulario con los datos enviados
        form = LoginForm(request, data=request.POST)

        # Permitir email: si el usuario ingresó email en 'username', intentar resolverlo a username real
        username_input = request.POST.get('username', '').strip()
        if '@' in username_input:
            try:
                related_user = User.objects.get(email__iexact=username_input)
                # Construir un dict de datos para el form, sin modificar request.POST
                data = request.POST.copy()
                data['username'] = related_user.username
                form = LoginForm(request, data=data)
            except User.DoesNotExist:
                print("No existe usuario con ese email")
                # Dejar que el form falle normalmente con el username ingresado
                pass

        if form.is_valid():
            print("Formulario válido")
            user = form.get_user()
            login(request, user)
            # Recordarme: si no se marca, la sesión expira al cerrar navegador
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            messages.success(request, 'Has iniciado sesión correctamente.')
            if request.user.is_staff and request.user.is_superuser:
                # Redirigir a la página de Django admin si es admin
                return redirect('/admin/')
            else:
                return redirect('perfil')
        else:
            print(form.errors)
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html', {'form': form, })


@login_required
def perfil_view(request):
    user_profile = UserProfile.objects.select_related(
        'user').filter(user=request.user).first()
    if not user_profile:
        messages.error(request, "El perfil de usuario no existe.")
        return redirect('login')
    return render(request, 'perfil.html', {'user': user_profile})
