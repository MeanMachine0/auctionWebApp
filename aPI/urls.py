from django.urls import path
from aPI import views

urlpatterns = [
    path("users/", views.getUsers, name="getUsers"),
    path("users/<int:pk>/", views.getUser, name="getUser"),
    path("accounts/", views.getAccounts, name="getAccounts"),
    path("accounts/<int:pk>", views.getAccount, name="getAccount"),
    path("items/", views.getItems, name="getItems"),
    path("items/<int:pk>", views.getItem, name="getItem"),
    path("endedItems/", views.getEndedItems, name="getEndedItems"),
    path("endedItems/<int:pk>", views.getEndedItem, name="getEndedItem"),
]