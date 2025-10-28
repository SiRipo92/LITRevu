from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # this replaces TemplateView
    path("register/", views.register, name="register"),
]
