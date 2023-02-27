import re
from django.shortcuts import render, redirect
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

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

def about(request):
    return render(request, "hello/about.html")

def contact(request):
    return render(request, "hello/contact.html")

def buy(request):
    items = ListItem.objects.all()
    return render(request, "hello/buy.html", {"items": items})

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
            return redirect('buy')
    else:
        form = ListItemForm()
    return render(request, 'hello/listAnItem.html', {'form': form})

def hello_there(request, name):
    return render(
        request,
        "hello/hello_there.html",
        {
            "name": name,
            "date": datetime.now()
        }
    )

def log_message(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "hello/log_message.html", {"form": form})
    
