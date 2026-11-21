import logging
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import UserLoginForm, UserProfileForm, UserRegisterForm
from users.models import User

logger = logging.getLogger(__name__)


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def dispatch(self, request, *args, **kwargs):
        # Уже вошедшему пользователю регистрироваться незачем
        if request.user.is_authenticated:
            return redirect("catalog:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        self.send_welcome_email(user)
        return response

    def send_welcome_email(self, user):
        try:
            send_mail(
                subject="Добро пожаловать в Skystore!",
                message=(
                    "Здравствуйте!\n\n"
                    f"Вы зарегистрировались в Skystore с адресом {user.email}.\n"
                    "Теперь вам доступны страницы товаров: просмотр, добавление и редактирование.\n\n"
                    "Команда Skystore"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except (smtplib.SMTPException, OSError) as error:
            # Регистрация уже прошла — не роняем страницу, а сообщаем о проблеме с письмом
            logger.exception("Не удалось отправить приветственное письмо: %s", error)
            messages.warning(
                self.request,
                "Вы зарегистрированы, но приветственное письмо отправить не удалось.",
            )
        else:
            messages.success(
                self.request,
                f"Регистрация прошла успешно! Письмо отправлено на {user.email}.",
            )


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Вы вошли в аккаунт.")
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        # Пользователь редактирует только свой профиль
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль сохранён.")
        return super().form_valid(form)
