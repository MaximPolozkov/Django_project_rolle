import re

from django import forms
from django.core.files.uploadedfile import UploadedFile

from catalog.models import Contact, Product

# Слова, которые нельзя использовать в названии и описании товара
FORBIDDEN_WORDS = (
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
)

ALLOWED_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")
ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png")
MAX_IMAGE_SIZE_MB = 5


class StyleFormMixin:
    """Добавляет Bootstrap-классы всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"


def validate_image_file(image):
    """Проверяет загруженную картинку: только JPEG или PNG, не больше 5 МБ."""
    # Проверяем только новый загруженный файл; уже сохранённую картинку не трогаем
    if not isinstance(image, UploadedFile):
        return image

    extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
    content_type = getattr(image, "content_type", "")
    if extension not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
        raise forms.ValidationError(
            f"Файл «{image.name}» не подходит: можно загрузить только JPEG или PNG."
        )

    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        size_mb = image.size / (1024 * 1024)
        raise forms.ValidationError(
            f"Файл слишком большой: {size_mb:.1f} МБ. "
            f"Максимальный размер — {MAX_IMAGE_SIZE_MB} МБ."
        )
    return image


def find_forbidden_words(text):
    """Возвращает запрещённые слова, найденные в тексте (без учёта регистра)."""
    text = (text or "").lower().replace("ё", "е")
    return [word for word in FORBIDDEN_WORDS if word in text]


class ProductForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "image", "category", "price", "is_published")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = "Название товара"
        self.fields["description"].widget.attrs.update(
            {"placeholder": "Описание товара", "rows": 4}
        )
        self.fields["price"].widget.attrs.update({"placeholder": "0.00", "step": "0.01"})
        self.fields["image"].widget.attrs["accept"] = "image/jpeg,image/png"
        self.fields["image"].help_text = (
            f"JPEG или PNG, не больше {MAX_IMAGE_SIZE_MB} МБ."
        )
        self.fields["category"].empty_label = "Без категории"

    def _check_forbidden(self, field_name, field_label):
        value = self.cleaned_data.get(field_name)
        found = find_forbidden_words(value)
        if found:
            raise forms.ValidationError(
                f"{field_label} содержит запрещённые слова: {', '.join(found)}. "
                "Уберите их и попробуйте снова."
            )
        return value

    def clean_name(self):
        return self._check_forbidden("name", "Название")

    def clean_description(self):
        return self._check_forbidden("description", "Описание")

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError(
                f"Цена не может быть отрицательной (вы ввели {price}). "
                "Укажите цену 0 или больше."
            )
        return price

    def clean_image(self):
        return validate_image_file(self.cleaned_data.get("image"))


class ContactForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("name", "phone", "message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = "Ваше имя"
        self.fields["phone"].widget.attrs["placeholder"] = "+7 900 000-00-00"
        self.fields["message"].widget.attrs.update({"placeholder": "Сообщение", "rows": 4})
        # Все поля обязательны
        for field in self.fields.values():
            field.required = True

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Имя должно содержать хотя бы 2 символа.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"\+?[\d\s\-()]{10,20}", phone):
            raise forms.ValidationError(
                "Введите телефон: только цифры, пробелы, «+», «-» и скобки, от 10 символов."
            )
        return phone

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 5:
            raise forms.ValidationError("Сообщение слишком короткое.")
        return message
