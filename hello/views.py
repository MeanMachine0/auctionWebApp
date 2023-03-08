from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import datetime
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models import Q
from .models import LogMessage, EndedItems, Items, Accounts
from .forms import LogMessageForm, ItemsForm, BrowseForm, BidForm

def getUsernameBalance(request):
    username = None
    balance = None
    if request.user.is_authenticated:
        username = request.user.username
        pK = request.user.pk
        balance = Accounts.objects.get(user__pk=pK).balance
    return (username, balance)

class HomeListView(ListView):
    model = EndedItems
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
    balance = getUsernameBalance(request)[1]
    if request.method == "POST":
        bidForm = BidForm(request.POST)
        item = Items.objects.get(pk=pk)
        if request.user.is_authenticated:
            if bidForm.is_valid():
                bid = bidForm.cleaned_data["bid"]
                minPrice = item.price + item.bidIncrement
                if bid >= minPrice and balance >= bid:
                    item.price = bid
                    item.numBids += 1
                    item.buyerId = Accounts.objects.get(user__pk=request.user.pk)
                    item.save()
                    message = "Bid Submitted."
                elif bid < minPrice:
                    message = "Could not submit bid: bid < £" + str(minPrice) + "."
                elif bid > balance:
                    message = "Could not submit bid: balance < bid."
                context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance), "message": message}
        else:
            return redirect("/login/")
    else:
        item = get_object_or_404(Items, pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance)}

    return render(request, "hello/itemDetail.html", context)
    

def about(request):
    return render(request, "hello/about.html", {"username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def myListings(request):
    pK = request.user.pk
    username = getUsernameBalance(request)[0]
    myCurrentItems = Items.objects.filter(sellerId=pK) 
    myOldItems = EndedItems.objects.filter(sellerId=username)

    return render(
        request, "hello/myListings.html", 
        {
        "username": username,
        "balance": str(getUsernameBalance(request)[1]),
        "myCurrentItems": myCurrentItems, 
        "myOldItems": myOldItems,
        }
        )

def browse(request):
    if request.method == "POST":
        browseForm = BrowseForm(request.POST)
        if browseForm.is_valid():
            items = Items.objects.all()
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
                "username": getUsernameBalance(request)[0],
                "balance": str(getUsernameBalance(request)[1]),
                }
            return render(request, "hello/browse.html", context)
        
    else:
        browseForm = BrowseForm()
        items = Items.objects.all()
        context = {
            "items": items.order_by("id"), 
            "browseForm": browseForm,
            "username": getUsernameBalance(request)[0],
            "balance": str(getUsernameBalance(request)[1]),
            }
        return render(request, "hello/browse.html", context)

def listAnItem(request):
    if request.method == "POST":
        form = ItemsForm(request.POST)
        if request.user.is_authenticated:
            if form.is_valid():
                item_data = form.cleaned_data
                item = Items.objects.create(
                    name=item_data["name"],
                    price=item_data["price"],
                    postageCost=item_data["postageCost"],
                    bidIncrement=item_data["bidIncrement"],
                    condition=item_data["condition"],
                    endDateTime=item_data["endDateTime"],
                    acceptReturns=item_data["acceptReturns"],
                    description=item_data["description"],
                    sellerId=Accounts.objects.get(user__pk=request.user.pk),
                )
                return redirect("itemListed/" + str(item.pk) + "/")
        else:
            return redirect("/login/")
    else:
        form = ItemsForm()
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
    item = get_object_or_404(Items, pk=pk)
    return render(request, "hello/itemListed.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def endedItemDetail(request, pk):
    item = get_object_or_404(EndedItems, pk=pk)
    return render(request, "hello/endedItemDetail.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})