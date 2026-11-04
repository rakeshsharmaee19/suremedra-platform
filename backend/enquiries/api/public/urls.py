from django.urls import path

from . import views

urlpatterns = [
    path("enquiries", views.EnquiryCreateView.as_view(), name="public-enquiry-create"),
]
