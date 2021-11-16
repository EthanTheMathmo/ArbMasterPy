from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("summary", views.summary, name="summary"),
    path("add_to_blacklist", views.add_to_blacklist, name="add_to_blacklist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("remove_from_blacklist", views.remove_from_blacklist, name="remove_from_blacklist"),
    path("generate_results", views.generate_results, name="generate_results"),
    path("userpage", views.userpage, name="userpage"),
    path("webhook", views.webhook, name="webhook"),
    path("purchases", views.purchases, name="purchases")

]
