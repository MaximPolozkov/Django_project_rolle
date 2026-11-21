import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from catalog.forms import StyleFormMixin, validate_image_file
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Регистрация: email, пароль и подтверждение пароля."""

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"placeholder": "you@example.com", "autofocus": True}
        )
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password2"].help_text = "Введите тот же пароль ещё раз."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже зарегистрирован. Войдите или укажите другой email."
            )
        return email


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    """Вход по email и паролю."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "placeholder": "you@example.com"}),
    )

    error_messages = {
        "invalid_login": "Неверный email или пароль. Проверьте данные и попробуйте снова.",
        "inactive": "Этот аккаунт отключён.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].label = "Пароль"


class UserProfileForm(StyleFormMixin, forms.ModelForm):
    """Редактирование профиля."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "country", "avatar")
        labels = {"first_name": "Имя", "last_name": "Фамилия"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone_number"].widget.attrs["placeholder"] = "+7 900 000-00-00"
        self.fields["avatar"].widget.attrs["accept"] = "image/jpeg,image/png"
        self.fields["avatar"].help_text = "JPEG или PNG, не больше 5 МБ."

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if phone and not re.fullmatch(r"\+?[\d\s\-()]{10,20}", phone):
            raise forms.ValidationError(
                "Введите телефон: только цифры, пробелы, «+», «-» и скобки, от 10 символов."
            )
        return phone or None

    def clean_avatar(self):
        return validate_image_file(self.cleaned_data.get("avatar"))
