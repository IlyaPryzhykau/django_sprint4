from django import forms
from django.utils import timezone

from .models import Post


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()
        )

    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'location', 'category', 'pub_date']
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d%H:%M', attrs={'type': 'datetime-local'}
            )
        }