from django import forms
from adopcion.models import Adoption

class AdoptionForm(forms.ModelForm):
    class Meta:
        model = Adoption
        fields = [ 'adopterName', 'adopterEmail', 'adopterPhone', 'message']  # 'pet' y 'responsable' se asignan en la vista
        widgets = {
            
            'adopterName': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint',
                'maxlength': 40,
                'placeholder': 'Tu nombre completo',
                'label': 'Nombre del adoptante',
            }),
            'adopterEmail': forms.EmailInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint',
                'maxlength': 100,
                'placeholder': 'Tu correo electrónico',
                'label': 'Email del adoptante',
            }),
            'adopterPhone': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint',
                'maxlength': 20,
                'placeholder': 'Tu número de teléfono',
                'label': 'Teléfono del adoptante',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint h-24 resize-none',
                'rows': 4,
                'maxlength': 150,
                'placeholder': 'Cuéntanos sobre ti y por qué quieres adoptar a nuestro amigo peludo...',
                'label': 'Mensaje',
            }),
        }