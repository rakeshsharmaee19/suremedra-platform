from django.urls import path

from . import views

urlpatterns = [
    path("formulations", views.FormulationListView.as_view(), name="public-formulation-list"),
    path("formulations/<slug:slug>", views.FormulationDetailView.as_view(), name="public-formulation-detail"),
    path("filters", views.FilterOptionsView.as_view(), name="public-filters"),
    path("compositions", views.CompositionSuggestView.as_view(), name="public-compositions"),
]
