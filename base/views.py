from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models import Q
from .models import Item, Account
from .forms import ItemsForm, BrowseForm, BidForm
from django.db.models.functions import Lower

def getUsernameBalance(request):
    username = None
    balance = None
    if request.user.is_authenticated:
        username = request.user.username
        pK = request.user.pk
        balance = Account.objects.get(user__pk=pK).balance
    return (username, balance)

class HomeListView(ListView):
    model = Item
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
        item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
        if request.user.is_authenticated:
            if bidForm.is_valid():
                bid = bidForm.cleaned_data["bid"]
                minPrice = item.price + item.bidIncrement
                buyerId = Account.objects.get(user__pk=request.user.pk).pk
                sellerId = item.seller_id
                if bid >= minPrice and balance >= bid and buyerId != sellerId and timezone.now() < item.endDateTime:
                    item.price = bid
                    item.numBids += 1
                    item.buyer = Account.objects.get(user__pk=request.user.pk)
                    bidders=item.getBidders()
                    bidders.append(item.buyer_id)
                    item.setBidders(bidders)
                    item.save()
                    message = "Bid Submitted."
                elif buyerId == sellerId:
                    message = "Could not submit bid: you listed this item."
                elif timezone.now() >= item.endDateTime:
                    message = "Could not submit bid: listing has ended."
                elif bid < minPrice:
                    message = "Could not submit bid: bid < £" + str(minPrice) + "."
                elif bid > balance:
                    message = "Could not submit bid: balance < bid."
                context={"bidForm": bidForm, "item": item, "username": username, "balance": str(balance), "message": message}
            else: 
                item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
                bidForm = BidForm()
                context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance)}
        else:
            return redirect("/login/")
    else:
        item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance)}

    return render(request, "base/itemDetail.html", context)
    

def about(request):
    return render(request, "base/about.html", {"username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def userBids(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    items = Item.objects.filter(ended=False).order_by("endDateTime")
    myCurrentItems = []
    for item in items:
        if request.user.pk in item.getBidders():
            myCurrentItems.append(item)
    eItems = Item.objects.filter(ended=True).order_by("-endDateTime")
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
    myCurrentItems = Item.objects.filter(Q(ended=False) & Q(seller=pk)).order_by("endDateTime")
    myOldItems = Item.objects.filter(Q(ended=True) & Q(seller=pk)).order_by("-endDateTime")
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

def browse(request, page):
    minItem = page * 100 - 100
    maxItem = page * 100
    if request.method == "POST":
        browseForm = BrowseForm(request.POST)
        if browseForm.is_valid():
            items = Item.objects.filter(ended=False)
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
            ascending = browseForm.cleaned_data["ascending"]
           
            if browseForm.cleaned_data["sortBy"] == "name":
                sortedAndFilteredItems = filteredItems.order_by(Lower('name'))[minItem:maxItem] if ascending else items.order_by(Lower('name').desc())[minItem:maxItem]
            elif ascending:
                sortedAndFilteredItems = filteredItems.order_by(browseForm.cleaned_data["sortBy"])[minItem:maxItem]
            else:
                sortedAndFilteredItems = filteredItems.order_by(f"-{browseForm.cleaned_data['sortBy']}")[minItem:maxItem]
            
            context = {
                "items": sortedAndFilteredItems,
                "browseForm": browseForm,
                "username": getUsernameBalance(request)[0],
                "balance": str(getUsernameBalance(request)[1]),
                "page": page,
                }
            return render(request, "base/browse.html", context)
        
    else:
        browseForm = BrowseForm()
        items = Item.objects.filter(ended=False)
        context = {
            "items": items.order_by("price")[minItem:maxItem], 
            "browseForm": browseForm,
            "username": getUsernameBalance(request)[0],
            "balance": str(getUsernameBalance(request)[1]),
            }
        return render(request, "base/browse.html", context)

def listAnItem(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    elif request.method == "POST":
        form = ItemsForm(request.POST)
        if form.is_valid():
            itemData = form.cleaned_data
            item = Item.objects.create(
                name=itemData["name"],
                price=itemData["price"],
                postageCost=itemData["postageCost"],
                bidIncrement=itemData["bidIncrement"],
                condition=itemData["condition"],
                endDateTime=itemData["endDateTime"],
                acceptReturns=itemData["acceptReturns"],
                description=itemData["description"],
                seller=Account.objects.get(pk=request.user.pk),
                category=itemData["category"],
            )
            return redirect("itemListed/" + str(item.pk) + "/")
    else:
        form = ItemsForm()
    return render(request, "base/listAnItem.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
    
def itemListed(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, "base/itemListed.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def endedItemDetail(request, pk):
    item = get_object_or_404(Item.objects.filter(ended=True), pk=pk)
    return render(request, "base/endedItemDetail.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})