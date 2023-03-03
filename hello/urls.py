from django.urls import path
from hello import views
from .models import LogItem
from hello.models import LogMessage

homeListView = views.HomeListView.as_view(
    queryset=LogItem.objects.order_by("-soldDateTime")[:100],
    context_object_name="itemList",
    template_name="hello/home.html",
)

messageListView = views.MessageListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],
    context_object_name="messageList",
    template_name="hello/messages.html",
)

urlpatterns = [
    path("", homeListView, name="home"),
    path("login/", views.loginView, name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("hello/<name>", views.helloThere, name="helloThere"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.logMessage, name="logMessage"),
    path("browse/", views.browse, name="browse"),
    path("listAnItem/", views.listAnItem, name="listAnItem"),
    path("browse/<int:pk>/", views.itemDetail, name="itemDetail"),
    path("listAnItem/itemListed/<int:pk>/", views.itemListed, name="itemListed"),
    path("messages/", messageListView, name="messages"),
]