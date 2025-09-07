# network/forms.py
from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    # Вместо ImageField — FileField (без жёсткой валидации Pillow)
    image = forms.FileField(required=False)

    class Meta:
        model = Post
        fields = ("text", "image")
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Что нового?"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Напишите комментарий…"}),
        }
