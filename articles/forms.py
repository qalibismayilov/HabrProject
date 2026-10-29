
from django import forms
from .models import Article, ArticleRevision


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "image", "content", "category"]

        labels = {
            "title": "Məqalənin başlığı",
            "image": "Məqalənin şəkli",
            "content": "Məqalənin mətni",
            "category": "Kateqoriya",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Məqalənin başlığını daxil et",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Məqalənin mətnini daxil et",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
        }


class ArticleRevisionForm(forms.ModelForm):
    class Meta:
        model = ArticleRevision
        fields = ["title", "image", "content", "category"]

        labels = {
            "title": "Yeni başlıq",
            "image": "Yeni şəkil (dəyişmək istəmirsənsə, boş saxla)",
            "content": "Yeni mətn",
            "category": "Yeni kateqoriya",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Yeni başlığı daxil et",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Yeni mətni daxil et",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
