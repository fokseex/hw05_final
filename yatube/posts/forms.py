from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст записи',
            'group': 'Группа',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Здесь отображается текст записи',
            'group': 'Группа к которой относится пост',
            'image': 'Изображение поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Здесь отображается текст комментария'
        }
