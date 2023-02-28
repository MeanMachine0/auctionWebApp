from django.urls import path
from hello import views
from hello.models import LogMessage

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="hello/home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("hello/<name>", views.helloThere, name="helloThere"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("log/", views.logMessage, name="logMessage"),
    path("browse/", views.browse, name="browse"),
    path("listAnItem/", views.listAnItem, name="listAnItem"),
    path("browse/<int:pk>/", views.itemDetail, name="itemDetail"),
    path("listAnItem/itemListed/<int:pk>/", views.itemListed, name="itemListed"),
]