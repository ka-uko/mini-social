from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ServiceTag
from django.db.models import Case, When, IntegerField

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("avatar", "bio", "role", "services", "city")
        labels = {
            "avatar": "Фотография (аватар)",
            "bio": "О себе",
            "role": "Тип пользователя",
            "services": "Специализации",
            "city": "Город",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Пару строк о себе..."}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "services": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Жёстко задаём порядок: Пармастер → Массаж → Аренда
        ordering = Case(
            When(code="parmaster", then=0),
            When(code="massage", then=1),
            When(code="rent", then=2),
            default=99,
            output_field=IntegerField(),
        )
        self.fields["services"].queryset = ServiceTag.objects.all().order_by(ordering, "title")

        # Подсказка к полю role
        self.fields["role"].help_text = "Если вы оказываете услуги — выберите специализации ниже."

        # Если роль не provider — можно скрыть поле в шаблоне (JS), но также чистим на уровне формы:
        role_val = (self.instance.role if self.instance else None)
        if role_val != "provider":
            # визуально мы спрячем в шаблоне; здесь важно — логика сохранения (см. clean)
            pass

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        services = cleaned.get("services")
        if role != "provider":
            # если не провайдер — не даём сохранять специализации
            cleaned["services"] = []
        return cleaned

