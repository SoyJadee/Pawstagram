from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    is_foundation = forms.BooleanField(required=False, label="¿Eres una fundación?")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "phone",
            "is_foundation",
        ]
        common_classes = 'w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all text-sm bg-white placeholder-gray-400 outline-none'
        widgets = {
            'password1': forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': common_classes, 'placeholder': 'Contraseña (mín. 8 caracteres)','maxlength': 20}),
            'password2': forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': common_classes, 'placeholder': 'Repite la contraseña','maxlength': 20}),
            'email': forms.EmailInput(attrs={'class': common_classes, 'placeholder': 'tu@email.com'}),
            'username': forms.TextInput(attrs={'class': common_classes, 'placeholder': '@tunombre'}),
            'first_name': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Tu apellido'}),
            'phone': forms.TextInput(attrs={'class': common_classes, 'placeholder': 'Tu teléfono'}),
            'is_foundation': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-paw-teal rounded focus:ring-2 focus:ring-paw-teal focus:ring-offset-0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Atributos comunes para todos los campos
        for name, field in self.fields.items():
            existing = field.widget.attrs
            existing.setdefault("class", "input-field")
            existing["required"] = "required" if field.required else ""
        # Tipos y patrones específicos
        self.fields["email"].widget.attrs["type"] = "email"
        self.fields["phone"].widget.attrs["pattern"] = "[0-9]+"
        # Accesibilidad: labels asociadas
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("aria-label", field.label or name)

    # Placeholders y autocomplete semántico

        mapping_autocomplete = {
            "username": "username",
            "email": "email",
            "first_name": "given-name",
            "last_name": "family-name",
            "phone": "tel",
            "password1": "new-password",
            "password2": "new-password",
        }
        for fname, ac in mapping_autocomplete.items():
            if fname in self.fields:
                self.fields[fname].widget.attrs["autocomplete"] = ac

class LoginForm(AuthenticationForm):
    """Formulario de login con estilos Tailwind.

    Nota: AuthenticationForm no respeta Meta.widgets, por lo que configuramos attrs en __init__.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        username_widget = self.fields['username'].widget
        password_widget = self.fields['password'].widget

        username_widget.attrs.setdefault('class', 'w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all')
        username_widget.attrs.setdefault('placeholder', 'Tu email o usuario')
        username_widget.attrs.setdefault('maxlength', '150')
        username_widget.attrs.setdefault('autocomplete', 'username')

        password_widget.attrs.setdefault('class', 'w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all')
        password_widget.attrs.setdefault('placeholder', '••••••••')
        password_widget.attrs.setdefault('maxlength', '20')
        password_widget.attrs.setdefault('autocomplete', 'current-password')