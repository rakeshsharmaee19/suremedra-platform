from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import health

admin.site.site_header = "Suremedra Admin"
admin.site.site_title = "Suremedra Admin"
admin.site.index_title = "Catalogue, enquiries and invoices"

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/health", health),
    path("api/v1/public/", include("config.urls_public")),
    path("api/v1/cms/", include("config.urls_cms")),
]

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    ]
