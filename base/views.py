import ast
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.shortcuts import redirect
from django.views.generic import ListView
from django.db.models import Q
from .models import Item, Account
from .forms import ItemForm, BrowseForm, BidForm
from django.db.models.functions import Lower
from firebase_admin import storage

bucket = storage.bucket()
toBool = {
    'true': True,
    'false': False,
}

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
    blob = bucket.blob(f'uploads/images/{pk}/smallerImage')
    url = blob.generate_signed_url(datetime.utcnow() + timedelta(seconds=30))
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
                context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance), "imgURL": url,}
        else:
            return redirect("/login/")
    else:
        item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": getUsernameBalance(request)[0], "balance": str(balance), "imgURL": url,}

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
    searchParams = request.GET.copy()
    if request.method == "POST":
        browseForm = BrowseForm(request.POST)
        if browseForm.is_valid():
            conditionsFilter = ["", "", "", "", "", ""]
            for i in range(6):
                if browseForm.cleaned_data[browseForm.conditions[i]]:
                    conditionsFilter[i] = browseForm.conditions[i]
            searchParams.update({
                "search": browseForm.cleaned_data["search"],
                "category": browseForm.cleaned_data["category"],
                "sortBy": browseForm.cleaned_data["sortBy"],
                "asc": browseForm.cleaned_data["ascending"],
                "lT": browseForm.cleaned_data["lThan"],
                "gT": browseForm.cleaned_data["gThan"],
                "new": browseForm.cleaned_data["new"],
                "excellent": browseForm.cleaned_data["excellent"],
                "good": browseForm.cleaned_data["good"],
                "used": browseForm.cleaned_data["used"],
                "refurbished": browseForm.cleaned_data["refurbished"],
                "partsOnly": browseForm.cleaned_data["partsOnly"],
                "rA": browseForm.cleaned_data["areReturnsAccepted"],
                "rNA": browseForm.cleaned_data["areReturnsNotAccepted"],
                "conditionsFilter": conditionsFilter,
            })
            newURL = request.scheme + "://" + request.get_host() + '/browse/page1/?' + searchParams.urlencode()
            return redirect(newURL)
        
    else:
        minItem = page * 100 - 100
        maxItem = page * 100
        if len(searchParams) > 0:
            search = searchParams.get("search")
            category = searchParams.get("category")
            sortBy = searchParams.get("sortBy")
            ascending = toBool[searchParams.get("asc").lower()]
            lThan = float(searchParams.get("lT"))
            gThan = float(searchParams.get("gT"))
            conditionsFilter = ast.literal_eval(searchParams.get("conditionsFilter"))
            areReturnsAccepted = toBool[searchParams.get("rA").lower()]
            areReturnsNotAccepted = toBool[searchParams.get("rNA").lower()]
            browseDict = {
                "search": search,
                "category": category,
                "sortBy": sortBy,
                "ascending": ascending,
                "lThan": lThan,
                "gThan": gThan,
                "areReturnsAccepted": areReturnsAccepted,
                "areReturnsNotAccepted": areReturnsNotAccepted,
            }
            filteredItems = Item.objects.filter(Q(ended=False) & Q(name__icontains=browseDict["search"]) &
                                        Q(price__range=(browseDict["lThan"], browseDict["gThan"])) &
                                        (Q(condition = conditionsFilter[0]) | Q(condition = conditionsFilter[1]) |
                                        Q(condition = conditionsFilter[2]) | Q(condition = conditionsFilter[3]) |
                                        Q(condition = conditionsFilter[4]) | Q(condition = conditionsFilter[5])) &
                                        (Q(acceptReturns = (browseDict["areReturnsAccepted"] == True)) |
                                        Q(acceptReturns = (browseDict["areReturnsNotAccepted"] == False))))
            if browseDict["category"] != "all":
                filteredItems = filteredItems.filter(category = browseDict["category"])

            results = filteredItems.__len__()
            if minItem > results:
                return redirect("/404/")
            if results < maxItem:
                maxItem = results
            
            ascending = browseDict["ascending"]
            if browseDict["sortBy"] == "name":
                sortedAndFilteredItems = filteredItems.order_by(Lower('name'))[minItem:maxItem] if ascending else filteredItems.order_by(Lower('name').desc())[minItem:maxItem]
            else:
                sortedAndFilteredItems = filteredItems.order_by(browseDict["sortBy"])[minItem:maxItem] if ascending else filteredItems.order_by(f"-{browseDict['sortBy']}")[minItem:maxItem]
            items = sortedAndFilteredItems
            browseForm = BrowseForm(initial={
                "search": search,
                "category": category,
                "sortBy": sortBy,
                "ascending": ascending,
                "lThan": lThan,
                "gThan": gThan,
                "new": toBool[searchParams.get("new").lower()],
                "excellent": toBool[searchParams.get("excellent").lower()],
                "good": toBool[searchParams.get("good").lower()],
                "used": toBool[searchParams.get("used").lower()],
                "refurbished": toBool[searchParams.get("refurbished").lower()],
                "partsOnly": toBool[searchParams.get("partsOnly").lower()],
                "areReturnsAccepted": areReturnsAccepted,
                "areReturnsNotAccepted": areReturnsNotAccepted,
            })
        else:
            items = Item.objects.filter(ended=False).order_by("price")
            results = items.__len__()
            if minItem > results:
                return redirect("/404/")
            if results < maxItem:
                    maxItem = results
            items = items[minItem:maxItem]
            browseForm = BrowseForm()
        
        context = {
            "items": items, 
            "browseForm": browseForm,
            "username": getUsernameBalance(request)[0],
            "balance": str(getUsernameBalance(request)[1]),
            "currentPage": page,
            "pages": createPages(results),
            "minItem": minItem + 1,
            "maxItem": maxItem,
            "results": results,
            "searchParams": searchParams.urlencode(),
            }
        return render(request, "base/browse.html", context)

def createPages(results):
    numPages = int(results/100 + 1)
    pages = []
    if numPages > 1:
        for pageNum in range(numPages):
            pages.append(pageNum + 1)
    return pages

def listAnItem(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    elif request.method == "POST":
        form = ItemForm(request.POST)
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
        form = ItemForm()
    return render(request, "base/listAnItem.html", {"form": form, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
    
def itemListed(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, "base/itemListed.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})

def endedItemDetail(request, pk):
    item = get_object_or_404(Item.objects.filter(ended=True), pk=pk)
    return render(request, "base/endedItemDetail.html", {"item": item, "username": getUsernameBalance(request)[0], "balance": str(getUsernameBalance(request)[1])})
