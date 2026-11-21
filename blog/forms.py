from django import forms

from blog.models import BlogPost
from catalog.forms import StyleFormMixin


class BlogPostForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ("title", "content", "preview", "is_published")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["rows"] = 8
