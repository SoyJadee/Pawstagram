from django import forms
from index.models import Comment, Post
from common.forms_mixins import XSSCleanMixin

class CommentForm(XSSCleanMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]  # 'post' se envía como hidden desde la plantilla
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'w-full p-2 border border-gray-300 rounded-md',
                    'rows': 2,
                    'placeholder': 'Escribe un comentario...',
                }
            ),
        }

class PostForm(XSSCleanMixin, forms.ModelForm):
    # Campo extra para subir/cambiar imagen (no está mapeado al modelo directamente)
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'w-full text-gray-500 file:bg-paw-teal file:text-white file:px-4 file:py-2 file:rounded-lg file:border-0 file:cursor-pointer hover:file:bg-dark-mint transition-all',
                'accept': 'image/jpeg,image/png,image/gif,image/webp',
            }
        ),
        help_text='Sube una imagen (JPG, PNG, GIF o WEBP).',
    )

    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'w-full bg-gray-50 border-0 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#00F5D4] focus:bg-white transition-all duration-300 resize-none',
                    'rows': 4,
                    'placeholder': '¿Qué quieres contar?',
                }
            ),
        }

