import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from hello.forms import LogMessageForm
from hello.models import LogMessage
from django.views.generic import ListView
from hello.forms import ListItemForm
from hello.models import ListItem
from .forms import ListItemForm
from .models import ListItem
from .forms import BrowseForm
from django.db.models import Q

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context
     
def itemDetail(request, pk):
    item = get_object_or_404(ListItem, pk=pk)
    return render(request, "hello/itemDetail.html", {"item": item})

def about(request):
    return render(request, "hello/about.html")

def contact(request):
    return render(request, "hello/contact.html")

def browse(request):
    if request.method == "POST":
        browseForm = BrowseForm(request.POST)
        if browseForm.is_valid():
            items = ListItem.objects.all()
            itemsToDelete = items.filter(name="test")
            for item in itemsToDelete:
                item.delete()

            conditionsFilter = ["", "", "", "", "", ""]
            for i in range(6):
                if browseForm.cleaned_data[browseForm.conditions[i]] is True:
                    conditionsFilter[i] = browseForm.conditions[i]

            filteredItems = items.filter(Q(name__icontains=browseForm.cleaned_data["search"]) & Q(price__range=(browseForm.cleaned_data["lThan"], browseForm.cleaned_data["gThan"])) & (Q(condition = conditionsFilter[0]) | Q(condition = conditionsFilter[1]) | Q(condition = conditionsFilter[2]) | Q(condition = conditionsFilter[3]) | Q(condition = conditionsFilter[4]) | Q(condition = conditionsFilter[5])) & (Q(acceptReturns = (browseForm.cleaned_data["areReturnsAccepted"] == True)) | Q(acceptReturns = (browseForm.cleaned_data["areReturnsNotAccepted"] == False))))

            if browseForm.cleaned_data["ascending"] is True:
                sortedAndFilteredItems = filteredItems.order_by(browseForm.cleaned_data["sortBy"])  
            else:
                sortedAndFilteredItems = filteredItems.order_by(f"-{browseForm.cleaned_data['sortBy']}")

            context = {
                "items": sortedAndFilteredItems, 
                "browseForm": browseForm,
                }
            return render(request, "hello/browse.html", context)
        
    else:
        browseForm = BrowseForm()
        items = ListItem.objects.all()
        context = {
            "items": items.order_by("id"), 
            "browseForm": browseForm,
            }
        return render(request, "hello/browse.html", context)

def listAnItem(request):
    if request.method == "POST":
        form = ListItemForm(request.POST)
        if form.is_valid():
            item_data = form.cleaned_data
            item = ListItem.objects.create(
                name=item_data["name"],
                price=item_data["price"],
                postageCost=item_data["postageCost"],
                bidIncrement=item_data["bidIncrement"],
                condition=item_data["condition"],
                endDateTime=item_data["endDateTime"],
                acceptReturns=item_data["acceptReturns"],
                description=item_data["description"]
            )
            return redirect("itemListed/" + str(item.pk) + "/")
    else:
        form = ListItemForm()
    return render(request, "hello/listAnItem.html", {"form": form})

def helloThere(request, name):
    return render(
        request,
        "hello/helloThere.html",
        {
            "name": name,
            "date": datetime.now()
        }
    )

def logMessage(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "hello/logMessage.html", {"form": form})
    
def itemListed(request, pk):
    item = get_object_or_404(ListItem, pk=pk)
    return render(request, "hello/itemListed.html", {"item": item})