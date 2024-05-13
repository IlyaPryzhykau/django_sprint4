from django import forms
from django.utils import timezone

from .models import (Comment,
                     Post)


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Установка начального значения для поля pub_date
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%dT%H:%M')

    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'location', 'category', 'pub_date']
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',  # Формат для datetime-local
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
