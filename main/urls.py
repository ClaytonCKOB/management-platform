from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("client/", views.client, name="client"),
    path("tracking/", views.tracking, name="tracking"),
    path("embalagem/", views.packing, name="client"),
    path("peso/", views.tracking, name="tracking"),
]