from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from .models import Pet

class PetForm(forms.ModelForm):
    # Usamos ImageField en el formulario para subir archivo y luego guardamos la URL en el modelo.
    # No es obligatorio para permitir edición sin cambiar imagen; en creación lo validamos en la vista.
    profile_photo_url = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "w-full text-gray-500 file:bg-paw-teal file:text-white file:px-4 file:py-2 file:rounded-lg file:border-0 file:cursor-pointer hover:file:bg-dark-mint transition-all",
                "accept": "image/jpeg,image/png,image/gif,image/webp",
            }
        ),
        help_text="Sube una imagen de la mascota (JPG, PNG, GIF o WEBP).",
    )
    name = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$",
                "Solo letras, espacios y guiones permitidos.",
            ),
        ],
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "maxlength": 20,
                "required": True,
            }
        ),
    )
    age = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        widget=forms.NumberInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "min": 0,
                "max": 40,
                "required": True,
            }
        ),
    )
    breed = forms.CharField(
        max_length=50,
        required=True,
        validators=[
            RegexValidator(
                r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$",
                "Solo letras, espacios y guiones permitidos.",
            ),
        ],
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "maxlength": 50,
                "required": True,
            }
        ),
    )
    description = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "rows": 4,
                "maxlength": 200,
                "required": True,
                "placeholder": "Describe la personalidad, comportamiento y características especiales de la mascota...",
            }
        ),
    )

    class Meta:
        model = Pet
        fields = [
            'idPet',
            "profile_photo_url",
            "name",
            "age",
            "tipoAnimal",
            "breed",
            "gender",
            "is_available_for_adoption",
            "description",
            "vacunas",
            "desparasitacion",
            "sterilization",
            "microchip",
        ]
        widgets = {
            "idPet": forms.HiddenInput(),
            "tipoAnimal": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                    "required": True,
                }
            ),
            "gender": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                    "required": True,
                }
            ),
            "is_available_for_adoption": forms.CheckboxInput(
                attrs={"class": "h-5 w-5 text-paw-teal focus:ring-paw-teal"}
            ),
            "vacunas": forms.CheckboxInput(
                attrs={"class": "h-5 w-5 text-paw-teal focus:ring-paw-teal"}
            ),
            "desparasitacion": forms.CheckboxInput(
                attrs={"class": "h-5 w-5 text-paw-teal focus:ring-paw-teal"}
            ),
            "sterilization": forms.CheckboxInput(
                attrs={"class": "h-5 w-5 text-paw-teal focus:ring-paw-teal"}
            ),
            "microchip": forms.CheckboxInput(
                attrs={"class": "h-5 w-5 text-paw-teal focus:ring-paw-teal"}
            ),
        }
