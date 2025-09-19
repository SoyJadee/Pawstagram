from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserCreationForm
from django.contrib import messages
from django.db import IntegrityError, transaction
from .models import UserProfile

# Create your views here.

def register_view(request):
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
                messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "No se pudo crear el cliente (teléfono o cédula ya existe).")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = UserCreationForm()

    return render(request, "Registro.html", {"form": form})

def login_view(request):
    return render(request, "login.html")