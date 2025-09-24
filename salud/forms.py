from django import forms
from .models import Reviews

class ReviewForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-4 border border-gray-200 rounded-2xl focus:outline-none focus:border-mint',
            'placeholder': 'Tu correo electrónico...'
        }),
        required=True
    )

    class Meta:
        model = Reviews
        fields = ['comment', "email"]
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-200 rounded-2xl focus:outline-none focus:border-mint h-24 resize-none',
                'rows': 3,
                'maxlength': 500,
                'required': False,
                'placeholder': 'Comparte tu experiencia (opcional)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Comentario opcional en el servidor
        if 'comment' in self.fields:
            self.fields['comment'].required = False
        if self.initial.get('email'):
            self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        # Anti-inyección: no permitir caracteres peligrosos
        if any(c in email for c in [';', '--', '/*', '*/', "'", '"', '=']):
            raise forms.ValidationError("El correo contiene caracteres no permitidos.")
        return email

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        # Permitir vacío, pero si hay texto, validar longitud y patrones peligrosos
        if comment:
            if len(comment) < 3:
                raise forms.ValidationError("El comentario debe tener al menos 3 caracteres si se ingresa.")
            if len(comment) > 500:
                raise forms.ValidationError("El comentario es demasiado largo (máx. 500 caracteres).")
            # Anti-inyección SQL básica
            import re
            patrones_sql = [
                r"(--|;|/\*|\*/|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|UNION|OR|AND)\b)",
                r"(['\"=])"
            ]
            for patron in patrones_sql:
                if re.search(patron, comment, re.IGNORECASE):
                    raise forms.ValidationError("El comentario contiene caracteres o palabras no permitidas.")
        return comment