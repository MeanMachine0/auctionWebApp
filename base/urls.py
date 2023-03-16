from django.urls import path
from base import views
from .models import EndedItems

homeListView = views.HomeListView.as_view(
    queryset=EndedItems.objects.filter(sold=True).order_by("-endDateTime")[:100],
    context_object_name="itemList",
    template_name="base/home.html",
)

urlpatterns = [
    path("", homeListView, name="home"),
    path("<int:pk>/", views.endedItemDetail, name="endedItemDetail"),
    path("login/", views.loginView, name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("about/", views.about, name="about"),
    path("userBids/", views.userBids, name="userBids"),
    path("userListings/<int:pk>", views.userListings, name="userListings"),
    path("browse/", views.browse, name="browse"),
    path("listAnItem/", views.listAnItem, name="listAnItem"),
    path("browse/<int:pk>/", views.itemDetail, name="itemDetail"),
    path("listAnItem/itemListed/<int:pk>/", views.itemListed, name="itemListed"),
]