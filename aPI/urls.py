from django.urls import path
from aPI import views


urlpatterns = [
    path("api/users/", views.getUsers, name="getUsers"),
    path("api/users/<int:pk>/", views.getUser, name="getUser"),
    path("api/accounts/", views.getAccounts, name="getAccounts"),
    path("api/accounts/<int:pk>/", views.getAccount, name="getAccount"),
    path("api/accounts/<int:pk>/items/", views.getAccountItems, name="getAccountItems"),
    path("api/items/", views.getItems, name="getItems"),
    path("api/items/<int:pk>/", views.getItem, name="getItem"),
    path("api/endedItems/", views.getEndedItems, name="getEndedItems"),
    path("api/endedItems/<int:pk>/", views.getEndedItem, name="getEndedItem"),
    path("api/users/create/", views.createUser, name="createUser"),
    path("api/items/create/", views.createItem, name="createItem"),
    path("api/items/<int:pk>/bid/", views.submitBid, name="submitBid"),
    path("api/users/<int:pk>/del/", views.delUser, name="delUser"),
    path("api/items/<int:pk>/del/", views.delItem, name="delItem"),
    path("api/login/", views.login, name="tokenLogin"),
    path("api/logout/", views.logout, name="tokenLogout"),
    path("api/amITheBuyer/<int:pk>/", views.amITheBuyer, name="amITheBuyer"),
]