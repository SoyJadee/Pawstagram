from django import forms
from adopcion.models import Adoption
import re


class AdoptionForm(forms.ModelForm):
    class Meta:
        model = Adoption
        fields = ["adopterName", "adopterEmail", "adopterPhone", "message"]
        widgets = {
            "adopterName": forms.TextInput(
                attrs={
                    "class": "w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint",
                    "maxlength": 40,
                    "placeholder": "Tu nombre completo",
                    "label": "Nombre del adoptante",
                }
            ),
            "adopterEmail": forms.EmailInput(
                attrs={
                    "class": "w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint",
                    "maxlength": 100,
                    "placeholder": "Tu correo electrónico",
                    "label": "Email del adoptante",
                }
            ),
            "adopterPhone": forms.TextInput(
                attrs={
                    "class": "w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint",
                    "maxlength": 20,
                    "placeholder": "Tu número de teléfono",
                    "label": "Teléfono del adoptante",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint h-24 resize-none",
                    "rows": 4,
                    "maxlength": 150,
                    "placeholder": "Cuéntanos sobre ti y por qué quieres adoptar a nuestro amigo...",
                    "label": "Mensaje",
                }
            ),
        }

    def clean_adopterName(self):
        name = self.cleaned_data.get("adopterName")
        if not name or len(name.strip()) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", name):
            raise forms.ValidationError(
                "El nombre solo puede contener letras y espacios."
            )
        return name

    def clean_adopterPhone(self):
        phone = self.cleaned_data.get("adopterPhone")
        if not phone:
            raise forms.ValidationError("El teléfono es obligatorio.")
        if not re.match(r"^\+?\d{7,20}$", phone):
            raise forms.ValidationError(
                "El teléfono debe contener solo números y puede incluir el prefijo '+'."
            )
        return phone

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if not message or len(message.strip()) < 10:
            raise forms.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return message
