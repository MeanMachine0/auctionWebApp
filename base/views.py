from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.timezone import datetime
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models import Q
from .models import EndedItems, Items, Accounts
from .forms import ItemsForm, BrowseForm, BidForm

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
                return render(request, "base/login.html", {"form": form, "username": username})
    else:
        form = AuthenticationForm()
    return render(request, "base/login.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
     
def logoutView(request): 
    logout(request)
    return redirect("/")

def itemDetail(request, pk):
    username = getUsernameBalance(request)[0]
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
                    bidders=item.getBidders()
                    bidders.append(item.buyerId_id)
                    item.setBidders(bidders)
                    item.save()
                    message = "Bid Submitted."
                elif bid < minPrice:
                    message = "Could not submit bid: bid < £" + str(minPrice) + "."
                elif bid > balance:
                    message = "Could not submit bid: balance < bid."
                context={"bidForm": bidForm, "item": item, "username": username, "balance": str(balance), "message": message}
        else:
            return redirect("/login/")
    else:
        item = get_object_or_404(Items, pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance)}

    return render(request, "base/itemDetail.html", context)
    

def about(request):
    return render(request, "base/about.html", {"username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def userBids(request):
    items = Items.objects.all().order_by("endDateTime")
    myCurrentItems = []
    for item in items:
        if request.user.pk in item.getBidders():
            myCurrentItems.append(item)
    eItems = EndedItems.objects.all().order_by("-endDateTime")
    myOldItems = []
    for item in eItems:
        if request.user.pk in item.getBidders():
            myOldItems.append(item)

    return render(
        request, "base/userBids.html", 
        {
        "username": getUsernameBalance(request)[0],
        "balance": str(getUsernameBalance(request)[1]),
        "myCurrentItems": myCurrentItems, 
        "myOldItems": myOldItems,
        }
        )

def userListings(request, pk):
    myCurrentItems = Items.objects.filter(sellerId=pk).order_by("endDateTime")
    myOldItems = EndedItems.objects.filter(sellerId=pk).order_by("-endDateTime")
    you = True if request.user.pk == pk else False

    return render(
        request, "base/userListings.html", 
        {
        "username": getUsernameBalance(request)[0],
        "balance": str(getUsernameBalance(request)[1]),
        "myCurrentItems": myCurrentItems, 
        "myOldItems": myOldItems,
        "you": you,
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
            return render(request, "base/browse.html", context)
        
    else:
        browseForm = BrowseForm()
        items = Items.objects.all()
        context = {
            "items": items.order_by("id"), 
            "browseForm": browseForm,
            "username": getUsernameBalance(request)[0],
            "balance": str(getUsernameBalance(request)[1]),
            }
        return render(request, "base/browse.html", context)

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
                    sellerId=Accounts.objects.get(pk=request.user.pk),
                )
                return redirect("itemListed/" + str(item.pk) + "/")
        else:
            return redirect("/login/")
    else:
        form = ItemsForm()
    return render(request, "base/listAnItem.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
    
def itemListed(request, pk):
    item = get_object_or_404(Items, pk=pk)
    return render(request, "base/itemListed.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def endedItemDetail(request, pk):
    item = get_object_or_404(EndedItems, pk=pk)
    return render(request, "base/endedItemDetail.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})