from django.urls import path
from base import views

urlpatterns = [
    path("", views.homeView, name="home"),
    path("login/", views.loginView, name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("about/", views.about, name="about"),
    path("userBids/", views.userBids, name="userBids"),
    path("userListings/<int:pk>/", views.userListings, name="userListings"),
    path("browse/page<int:page>/", views.browse, name="browse"),
    path("listAnItem/", views.listAnItem, name="listAnItem"),
    path("browse/<int:pk>/", views.itemDetail, name="itemDetail"),
    path("listAnItem/itemListed/<int:pk>/", views.itemListed, name="itemListed"),
]