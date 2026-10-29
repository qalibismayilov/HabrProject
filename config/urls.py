
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django administration panel
    path("admin/", admin.site.urls),

    # User registration, login and logout
    path("accounts/", include("accounts.urls")),

    # Articles and main website pages
    path("", include("articles.urls")),
]

# Serve uploaded images during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
