from django.contrib import admin
from django.urls import path, include
from defects_app.views import custom_login_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", custom_login_view, name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("defects_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
