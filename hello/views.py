from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import datetime
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models import Q
from .models import LogMessage, LogItem, ListItem, Account
from .forms import LogMessageForm, ListItemForm, BrowseForm, BidForm

def getUsernameBalance(request):
    username = None
    balance = None
    if request.user.is_authenticated:
        username = request.user.username
        balance = Account.objects.all().get(user__username=username).balance
    return (username, balance)

class HomeListView(ListView):
    model = LogItem
    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        context["username"]  = getUsernameBalance(self.request)[0]
        context["balance"] = str(getUsernameBalance(self.request)[1])
        return context

class MessageListView(ListView):
    model = LogMessage

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        return context

AuthenticationForm.error_messages = {
    "invalid_login": "Invalid username and/or password.",
    "inactive": "This account is inactive."
}

def loginView(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("Logged in as " + username + ".")
                return redirect("/")
            else:
                username = None
                return render(request, "hello/login.html", {"form": form, "username": username})
    else:
        form = AuthenticationForm()
    return render(request, "hello/login.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
     
def logoutView(request): 
    logout(request)
    return redirect("/")

def itemDetail(request, pk):
    if request.method == "POST":
        bidForm = BidForm(request.POST)
        if bidForm.is_valid():
            item = ListItem.objects.all().get(pk=pk)

            context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])}
    else:
        item = get_object_or_404(ListItem, pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])}

    return render(request, "hello/itemDetail.html", context)
    

def about(request):
    return render(request, "hello/about.html", {"username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def contact(request):
    return render(request, "hello/contact.html", {"username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

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

            filteredItems = items.filter(Q(name__icontains=browseForm.cleaned_data["search"]) & 
                                         Q(price__range=(browseForm.cleaned_data["lThan"], browseForm.cleaned_data["gThan"])) & 
                                         (Q(condition = conditionsFilter[0]) | Q(condition = conditionsFilter[1]) | Q(condition = conditionsFilter[2]) | 
                                          Q(condition = conditionsFilter[3]) | Q(condition = conditionsFilter[4]) | Q(condition = conditionsFilter[5])) & 
                                          (Q(acceptReturns = (browseForm.cleaned_data["areReturnsAccepted"] == True)) | 
                                           Q(acceptReturns = (browseForm.cleaned_data["areReturnsNotAccepted"] == False))))

            if browseForm.cleaned_data["ascending"] is True:
                sortedAndFilteredItems = filteredItems.order_by(browseForm.cleaned_data["sortBy"])  
            else:
                sortedAndFilteredItems = filteredItems.order_by(f"-{browseForm.cleaned_data['sortBy']}")

            context = {
                "items": sortedAndFilteredItems, 
                "browseForm": browseForm,
                "username": getUsernameBalance(request),
                }
            return render(request, "hello/browse.html", context)
        
    else:
        browseForm = BrowseForm()
        items = ListItem.objects.all()
        context = {
            "items": items.order_by("id"), 
            "browseForm": browseForm,
            "username": getUsernameBalance(request)[0],
            "balance": str(getUsernameBalance(request)[1]),
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
    return render(request, "hello/listAnItem.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def helloThere(request, name):
    return render(
        request,
        "hello/helloThere.html",
        {
            "name": name,
            "date": datetime.now(),
            "username": getUsernameBalance(),
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
    return render(request, "hello/itemListed.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})