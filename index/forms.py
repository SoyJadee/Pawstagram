from django import forms
from index.models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # 'post' se envía como hidden desde la plantilla
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 2,
                'placeholder': 'Escribe un comentario...',
            }),
        }
