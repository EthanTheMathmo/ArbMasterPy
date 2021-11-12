from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("summary", views.summary, name="summary"),
    path("add_to_blacklist", views.add_to_blacklist, name="add_to_blacklist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout")
]
