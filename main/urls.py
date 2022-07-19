from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path("",  RedirectView.as_view(url='client/', permanent=False), name="index"),
    path("client/", views.client, name="client"),
    path("client/auvo/<int:id>", views.auvoPage, name="client"),
    path("client/sysop/<int:id>", views.sysopPage, name="client"),
    path("tracking/", views.tracking, name="tracking"),
    path("embalagem/", views.packing, name="client"),
    path("embalagem/<int:id>", views.packingView, name="client"),
    path("peso/", views.tracking, name="tracking"),
]