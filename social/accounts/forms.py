from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ServiceTag


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    # Явно объявляем поле, чтобы гарантировать корректную валидацию списка значений
    services = forms.ModelMultipleChoiceField(
        label="Специализации",
        queryset=ServiceTag.objects.all().order_by("title"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = User
        fields = ("avatar", "bio", "role", "services", "city")
        labels = {
            "avatar": "Аватар",
            "bio": "О себе",
            "role": "Тип пользователя",
            "services": "Специализации",
            "city": "Город",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select", "id": "id_role"}),
            # services виджет задан выше в поле
            "city": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Аватар не обязателен
        self.fields["avatar"].required = False
        # Убедимся, что queryset всегда полный и отсортирован (если кто-то поменяет в админке)
        self.fields["services"].queryset = ServiceTag.objects.all().order_by("title")

    # ВАЖНО: не перезаписываем cleaned["services"]!
    # Ранее тут был clean(), который обнулял services для ролей != provider.
    # Теперь сохраняем услуги для всех ролей (provider/builder/seller).
