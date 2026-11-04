from django.urls import include, path

urlpatterns = [
    path("", include("catalog.api.public.urls")),
    path("", include("enquiries.api.public.urls")),
]
