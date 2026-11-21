from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from catalog.forms import ContactForm, ProductForm
from catalog.models import Product

UNPUBLISH_PERMISSION = "catalog.can_unpublish_product"
DELETE_PERMISSION = "catalog.delete_product"


def visible_products(user):
    """Какие товары видит пользователь.

    Гость — только опубликованные; вошедший — опубликованные и свои;
    модератор — все, чтобы было что модерировать.
    """
    products = Product.objects.select_related("category", "owner")
    if user.has_perm(UNPUBLISH_PERMISSION):
        return products
    if user.is_authenticated:
        return products.filter(Q(is_published=True) | Q(owner=user))
    return products.filter(is_published=True)


def can_edit_product(user, product):
    """Редактировать товар может только его владелец."""
    return user.is_authenticated and product.owner_id == user.pk


def can_delete_product(user, product):
    """Удалить товар может владелец или модератор (право delete_product)."""
    return can_edit_product(user, product) or user.has_perm(DELETE_PERMISSION)


class HomeView(ListView):
    """Главная страница: список товаров."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"

    def get_queryset(self):
        return visible_products(self.request.user)


class ProductDetailView(DetailView):
    """Страница товара. Неопубликованный чужой товар вернёт 404."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return visible_products(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        product = self.object
        context["can_edit"] = can_edit_product(user, product)
        context["can_delete"] = can_delete_product(user, product)
        context["can_unpublish"] = product.is_published and user.has_perm(
            UNPUBLISH_PERMISSION
        )
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        # Владелец — текущий пользователь, его не выбирают в форме
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Товар «{self.object.name}» добавлен.")
        return response

    def get_success_url(self):
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def test_func(self):
        return can_edit_product(self.request.user, self.get_object())

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Товар «{self.object.name}» сохранён.")
        return response

    def get_success_url(self):
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("catalog:home")

    def test_func(self):
        return can_delete_product(self.request.user, self.get_object())

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f"Товар «{name}» удалён.")
        return response


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Модератор снимает товар с публикации (только POST)."""

    permission_required = UNPUBLISH_PERMISSION

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.is_published:
            product.is_published = False
            product.save(update_fields=["is_published", "updated_at"])
            messages.success(request, f"Товар «{product.name}» снят с публикации.")
        return redirect("catalog:product_detail", pk=product.pk)


class ContactsView(TemplateView):
    """Страница контактов с формой обратной связи."""

    template_name = "catalog/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", ContactForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(
                request, f"Спасибо, {contact.name}! Ваше сообщение отправлено."
            )
            # Перенаправление защищает от повторной отправки при обновлении страницы
            return redirect("catalog:contacts")
        # Форма с ошибками показывается снова
        return self.render_to_response(self.get_context_data(form=form))
