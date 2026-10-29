
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-poçt",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "E-poçt ünvanınızı daxil edin",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

        labels = {
            "username": "İstifadəçi adı",
            "first_name": "Ad",
            "last_name": "Soyad",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "İstifadəçi adınızı daxil edin",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Adınızı daxil edin",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Soyadınızı daxil edin",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].label = "Şifrə"
        self.fields["password2"].label = "Şifrəni təkrar daxil edin"

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Şifrənizi daxil edin",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Şifrənizi yenidən daxil edin",
        })

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]
        user.role = User.Role.USER

        if commit:
            user.save()

        return user
