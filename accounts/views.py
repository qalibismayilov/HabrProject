
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                "Qeydiyyat uğurla tamamlandı. İndi sistemə daxil ola bilərsən.",
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if user.is_blocked or not user.is_active:
                messages.error(
                    request,
                    "Hesabın bloklanıb və ya deaktiv edilib.",
                )
                return redirect("login")

            login(request, user)
            messages.success(request, "Sistemə uğurla daxil oldun.")
            return redirect("home")

        messages.error(
            request,
            "İstifadəçi adı və ya şifrə yanlışdır.",
        )

    return render(request, "accounts/login.html")


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Sistemdən uğurla çıxış etdin.")
    return redirect("home")
