from django import forms
from django.utils import timezone

from .models import (Comment,
                     ForbiddenWord,
                     Post)


def validate_content_forbidden_words(value):
    forbidden_words = set(ForbiddenWord.objects.values_list('word', flat=True))
    for word in forbidden_words:
        if word.lower() in value.lower():
            raise forms.ValidationError(f"{word} - запрещенное слово!")


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Установка начального значения для поля pub_date
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%dT%H:%M')

    def clean_title(self):
        text = self.cleaned_data.get('title')
        if text:
            validate_content_forbidden_words(self.cleaned_data.get('title'))
        return text

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if text:
            validate_content_forbidden_words(self.cleaned_data.get('text'))
        return text

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

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if text:
            validate_content_forbidden_words(self.cleaned_data.get('text'))
        return text

    class Meta:
        model = Comment
        fields = ('text',)
