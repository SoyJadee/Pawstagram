from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import re

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
        common_classes = "w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all text-sm bg-white placeholder-gray-400 outline-none"
        widgets = {
            "password1": forms.PasswordInput(
                attrs={
                    "autocomplete": "new-password",
                    "class": common_classes,
                    "placeholder": "Contraseña (mín. 8 caracteres)",
                    "maxlength": 20,
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "autocomplete": "new-password",
                    "class": common_classes,
                    "placeholder": "Repite la contraseña",
                    "maxlength": 20,
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": common_classes, "placeholder": "tu@email.com"}
            ),
            "username": forms.TextInput(
                attrs={"class": common_classes, "placeholder": "@tunombre"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": common_classes, "placeholder": "Tu nombre"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": common_classes, "placeholder": "Tu apellido"}
            ),
            "phone": forms.TextInput(
                attrs={"class": common_classes, "placeholder": "Tu teléfono"}
            ),
            "is_foundation": forms.CheckboxInput(
                attrs={
                    "class": "h-5 w-5 text-paw-teal rounded focus:ring-2 focus:ring-paw-teal focus:ring-offset-0"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unificar clases e IDs y manejar correctamente el atributo required
        common_classes = getattr(
            self.Meta,
            "common_classes",
            "w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all text-sm bg-white placeholder-gray-400 outline-none",
        )

        id_mapping = {
            "username": "username",
            "email": "email",
            "first_name": "first_name",
            "last_name": "last_name",
            "phone": "phone",
            "password1": "password",  # para toggle/medidor de fuerza
            "password2": "password2",
            "is_foundation": "is_foundation",
        }

        for name, field in self.fields.items():
            widget = field.widget
            # IDs consistentes para integración con JS/HTML
            if name in id_mapping:
                widget.attrs["id"] = id_mapping[name]

            # Marcar required solo cuando realmente lo es; eliminar si no
            if field.required:
                widget.attrs["required"] = ""
            else:
                widget.attrs.pop("required", None)

            # Aplicar clases tailwind uniformes a entradas de texto/email/password
            if not isinstance(widget, (forms.CheckboxInput,)):
                # Si ya hay clases, las sustituimos para asegurar uniformidad
                widget.attrs["class"] = common_classes

            # Accesibilidad
            widget.attrs.setdefault("aria-label", field.label or name)

        # Tipos y patrones específicos
        self.fields["email"].widget.attrs["type"] = "email"
        self.fields["phone"].widget.attrs["pattern"] = "[0-9]+"

        # Asegurar attrs específicos en passwords (UserCreationForm no siempre respeta Meta.widgets)
        p1 = self.fields.get("password1")
        if p1 is not None:
            p1.widget.attrs.update(
                {
                    "autocomplete": "new-password",
                    "placeholder": "Contraseña (mín. 8 caracteres)",
                    "maxlength": "20",
                    "id": "password",  # imprescindible para el toggle/medidor
                    "class": common_classes,
                }
            )

        p2 = self.fields.get("password2")
        if p2 is not None:
            p2.widget.attrs.update(
                {
                    "autocomplete": "new-password",
                    "placeholder": "Repite la contraseña",
                    "maxlength": "20",
                    "id": "password",
                    "class": common_classes,
                }
            )

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

    def clean_username(self):
        username = self.cleaned_data.get("username", "")
        if not re.match(r"^[\w.@+-]+$", username):
            raise forms.ValidationError(
                "El usuario solo puede contener letras, números y ./@/+-"
            )
        if self._contains_sql_injection(username):
            raise forms.ValidationError("El usuario contiene caracteres no permitidos.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", "")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$", first_name):
            raise forms.ValidationError(
                "El nombre solo puede contener letras, espacios y guiones."
            )
        if self._contains_sql_injection(first_name):
            raise forms.ValidationError("El nombre contiene caracteres no permitidos.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name", "")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$", last_name):
            raise forms.ValidationError(
                "El apellido solo puede contener letras, espacios y guiones."
            )
        if self._contains_sql_injection(last_name):
            raise forms.ValidationError(
                "El apellido contiene caracteres no permitidos."
            )
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        if self._contains_sql_injection(email):
            raise forms.ValidationError("El email contiene caracteres no permitidos.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not re.match(r"^\+?\d{7,15}$", phone):
            raise forms.ValidationError(
                "El teléfono debe contener solo números y puede incluir el prefijo '+'."
            )
        if self._contains_sql_injection(phone):
            raise forms.ValidationError(
                "El teléfono contiene caracteres no permitidos."
            )
        return phone

    def _contains_sql_injection(self, value):
        # Busca palabras clave y caracteres peligrosos
        patrones_sql = [
            r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
            r"(['\";=])",
        ]
        for patron in patrones_sql:
            if re.search(patron, value, re.IGNORECASE):
                return True
        return False


class LoginForm(AuthenticationForm):
    """Formulario de login con estilos Tailwind.
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        username_widget = self.fields["username"].widget
        password_widget = self.fields["password"].widget

        username_widget.attrs.setdefault(
            "class",
            "w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all",
        )
        username_widget.attrs.setdefault("placeholder", "Tu email o usuario")
        username_widget.attrs.setdefault("maxlength", "150")
        username_widget.attrs.setdefault("autocomplete", "username")

        password_widget.attrs.setdefault(
            "class",
            "w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all",
        )
        password_widget.attrs.setdefault("placeholder", "••••••••")
        password_widget.attrs.setdefault("maxlength", "20")
        password_widget.attrs.setdefault("autocomplete", "current-password")

    def clean_username(self):
        username = self.cleaned_data.get("username", "")
        if self._contains_sql_injection(username):
            raise forms.ValidationError("El usuario contiene caracteres no permitidos.")
        return username

    def _contains_sql_injection(self, value):
        patrones_sql = [
            r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
            r"(['\";=])",
        ]
        for patron in patrones_sql:
            if re.search(patron, value, re.IGNORECASE):
                return True
        return False


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "maxlength": 30,
                "required": True,
            }
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "maxlength": 30,
                "required": True,
            }
        ),
    )
    email = forms.EmailField(
        max_length=150,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                "maxlength": 150,
                "required": True,
            }
        ),
    )

    class Meta:
        model = UserProfile
        fields = ["phone"]
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-200 rounded-xl input-focus",
                    "required": True,
                    "maxlength": 15,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
        elif self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile.save()
        return profile

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", "")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$", first_name):
            raise forms.ValidationError(
                "El nombre solo puede contener letras, espacios y guiones."
            )
        if self._contains_sql_injection(first_name):
            raise forms.ValidationError("El nombre contiene caracteres no permitidos.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name", "")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s-]+$", last_name):
            raise forms.ValidationError(
                "El apellido solo puede contener letras, espacios y guiones."
            )
        if self._contains_sql_injection(last_name):
            raise forms.ValidationError(
                "El apellido contiene caracteres no permitidos."
            )
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        if self._contains_sql_injection(email):
            raise forms.ValidationError("El email contiene caracteres no permitidos.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not re.match(r"^\+?\d{7,15}$", phone):
            raise forms.ValidationError(
                "El teléfono debe contener solo números y puede incluir el prefijo '+'."
            )
        if self._contains_sql_injection(phone):
            raise forms.ValidationError(
                "El teléfono contiene caracteres no permitidos."
            )
        return phone

    def _contains_sql_injection(self, value):
        patrones_sql = [
            r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
            r"(['\";=])",
        ]
        for patron in patrones_sql:
            if re.search(patron, value, re.IGNORECASE):
                return True
        return False


class DeleteUserForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="Confirma tu email para eliminar la cuenta",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-paw-teal focus:border-transparent transition-all",
                "placeholder": "ejemplo@email.com",
                "maxlength": "150",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        if self._contains_sql_injection(email):
            raise forms.ValidationError("El email contiene caracteres no permitidos.")
        return email

    def _contains_sql_injection(self, value):
        patrones_sql = [
            r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
            r"(['\";=])",
        ]
        for patron in patrones_sql:
            if re.search(patron, value, re.IGNORECASE):
                return True
        return False
