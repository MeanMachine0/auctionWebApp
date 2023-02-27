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
from django.views.generic.detail import DetailView

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context
     
def itemDetail(request, pk):
    item = get_object_or_404(ListItem, pk=pk)
    return render(request, 'hello/itemDetail.html', {'item': item})

def about(request):
    return render(request, "hello/about.html")

def contact(request):
    return render(request, "hello/contact.html")

def browse(request):
    items = ListItem.objects.all()
    return render(request, "hello/browse.html", {"items": items})

def listAnItem(request):
    if request.method == 'POST':
        form = ListItemForm(request.POST)
        if form.is_valid():
            item_data = form.cleaned_data
            item = ListItem.objects.create(
                name=item_data['name'],
                startingPrice=item_data['startingPrice'],
                postageCost=item_data['postageCost'],
                bidIncrement=item_data['bidIncrement'],
                condition=item_data['condition'],
                endDateTime=item_data['endDateTime'],
                acceptReturns=item_data['acceptReturns'],
                description=item_data['description']
            )
            return redirect('itemListed')
    else:
        form = ListItemForm()
    return render(request, 'hello/listAnItem.html', {'form': form})

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
    
def itemListed(request):
    return render(request, "hello/itemListed.html")