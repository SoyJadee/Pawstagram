from django import forms
from adopcion.models import Adoption

class AdoptionForm(forms.ModelForm):
    class Meta:
        model = Adoption
        fields = [ 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-200 rounded-xl focus:outline-none focus:border-mint h-24 resize-none',
                'rows': 4,
                'maxlength': 150,
                'placeholder': 'Cuéntanos sobre ti y por qué quieres adoptar a nuestro amigo peludo...',
                'label': 'Mensaje',
            }),
        }