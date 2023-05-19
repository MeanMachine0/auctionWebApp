import ast
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.shortcuts import redirect
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
def getBaseUrl(request):
    baseUrl = f"{request.scheme}://{request.get_host()}"
    return baseUrl

def getLoginPath(request):
    loginParams = request.GET.copy()
    loginParams.update({
        "path": request.path,
    })
    loginPath = f"/login/?{loginParams.urlencode()}"
    return loginPath

def getDownloadUrl(path):
    blob = bucket.blob(path)
    url = blob.generate_signed_url(datetime.utcnow() + timedelta(hours=1))
    return url

def getUsernameBalance(request):
    username = None
    balance = None
    user = request.user
    if user.is_authenticated:
        username = user.username
        balance = str(Account.objects.get(user=user).balance)
        b1, b2 = balance.split('.')
        lb1 = len(b1)
        if lb1 >= 4:
            first = True
            indices = []
            while lb1 >= 3:
                lb1 = lb1 - 4 if first else lb1 - 3
                indices.append(lb1)
                first = False
            for index in indices:
                b1 = f"{b1[:index]}{b1[index]},{b1[index+1:]}"
            balance = '.'.join([b1, b2])     
    return (username, balance)

def homeView(request):
    username, balance = getUsernameBalance(request)
    items = Item.objects.filter(sold=True).order_by("-endDateTime")[:100]
    for item in items:
        item.bidders = getDownloadUrl(f"uploads/images/{item.id}/thumbNail")
    context = {
        "items": items,
        "username": username,
        "balance": balance,
        "home": True,
    }
    return render(request, 'base/browse.html', context)

AuthenticationForm.error_messages = {
    "invalid_login": "Invalid username and/or password.",
    "inactive": "This account is inactive."
}

def loginView(request):
    loginParams = request.GET.copy()
    path = loginParams.get("path")
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if path is not None:
                    if path == "/userListings/0/":
                        path = f"/userListings/{user.pk}/"
                    return redirect(path)
                else: 
                    return redirect("/")
            else:
                username = None
                return render(request, "base/login.html", {"form": form, "username": username})
    else:
        form = AuthenticationForm()
    username, balance = getUsernameBalance(request)
    return render(request, "base/login.html", {"form": form, "username": username, "balance": balance})
     
def logoutView(request): 
    logout(request)
    return redirect("/")

def itemDetail(request, pk):
    username, balance = getUsernameBalance(request)
    url = getDownloadUrl(f'uploads/images/{pk}/smallerImage')
    if request.method == "POST":
        bidForm = BidForm(request.POST)
        item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
        if request.user.is_authenticated:
            if bidForm.is_valid():
                account = Account.objects.get(user=request.user)
                balance = account.balance
                bid = bidForm.cleaned_data["bid"]
                minPrice = item.price + item.bidIncrement
                buyerId = account.id
                sellerId = item.seller_id
                if bid >= minPrice and balance >= bid and buyerId != sellerId and timezone.now() < item.endDateTime:
                    item.price = bid
                    item.numBids += 1
                    item.buyer = account
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
                balance = getUsernameBalance(request)[1]
                context={"bidForm": bidForm, "item": item, "username": username, "balance": balance, "message": message, "imgUrl": url,}
            else: 
                item = get_object_or_404(Item.objects.filter(ended=False), pk=pk)
                bidForm = BidForm()
                context={"bidForm": bidForm, "item": item, "username": username, "balance": balance, "imgUrl": url,}
        else:
            loginPath = getLoginPath(request)
            return redirect(loginPath)
    else:
        item = get_object_or_404(Item.objects.all(), pk=pk)
        bidForm = BidForm()
        context={"bidForm": bidForm, "item": item, "username": username, "balance": balance, "imgUrl": url,}
    active = not item.ended
    context["active"] = active
    return render(request, "base/itemDetail.html", context)
    

def about(request):
    username, balance = getUsernameBalance(request)
    return render(request, "base/about.html", {"username": username, "balance": balance})

def userBids(request):
    if not request.user.is_authenticated:
        loginPath = getLoginPath(request)
        return redirect(loginPath)
    username, balance = getUsernameBalance(request)
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
        "username": username,
        "balance": balance,
        "myCurrentItems": myCurrentItems, 
        "myOldItems": myOldItems,
        }
        )

def userListings(request, pk):
    if not request.user.is_authenticated and pk == 0:
        loginPath = getLoginPath(request)
        return redirect(loginPath)
    username, balance = getUsernameBalance(request)
    myCurrentItems = Item.objects.filter(Q(ended=False) & Q(seller=pk)).order_by("endDateTime")
    myOldItems = Item.objects.filter(Q(ended=True) & Q(seller=pk)).order_by("-endDateTime")
    you = True if request.user.pk == pk else False
    return render(
        request, "base/userListings.html", 
        {
        "username": username,
        "balance": balance,
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
            searchParams.clear()
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
                "n": browseForm.cleaned_data["showNItems"], 
                "conditionsFilter": conditionsFilter,
            })
            newUrl = f"{getBaseUrl(request)}/browse/page1/?{searchParams.urlencode()}"
            return redirect(newUrl)
        
    else:
        username, balance = getUsernameBalance(request)
        if len(searchParams) > 0:
            search = searchParams.get("search")
            category = searchParams.get("category")
            sortBy = searchParams.get("sortBy")
            ascending = toBool[searchParams.get("asc").lower()]
            lThan = float(searchParams.get("lT"))
            gThan = float(searchParams.get("gT"))
            areReturnsAccepted = toBool[searchParams.get("rA").lower()]
            areReturnsNotAccepted = toBool[searchParams.get("rNA").lower()]
            conditionsFilter = ast.literal_eval(searchParams.get("conditionsFilter"))
            n = int(searchParams.get("n"))
            minItem = page * n - n
            maxItem = page * n
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
                "showNItems": n,
            })
        else:
            n = 20
            minItem = page * n - n
            maxItem = page * n
            items = Item.objects.filter(ended=False).order_by("price")
            results = items.__len__()
            if minItem > results:
                return redirect("/404/")
            if results < maxItem:
                    maxItem = results
            items = items[minItem:maxItem]
            browseForm = BrowseForm()
        for item in items:
            item.bidders = getDownloadUrl(f'uploads/images/{item.id}/thumbNail')

        context = {
            "items": items, 
            "browseForm": browseForm,
            "username": username,
            "balance": balance,
            "currentPage": page,
            "pages": createPages(results, n),
            "minItem": minItem + 1,
            "maxItem": maxItem,
            "results": results,
            "searchParams": searchParams.urlencode(),
            }
        return render(request, "base/browse.html", context)

def createPages(results, n):
    numPages = results/n
    if numPages != int(numPages):
        numPages = int(numPages + 1)
    else: 
        numPages = int(numPages)
    pages = []
    if numPages > 1:
        for pageNum in range(numPages):
            pages.append(pageNum + 1)
    return pages

def listAnItem(request):
    if not request.user.is_authenticated:
        loginPath = getLoginPath(request)
        return redirect(loginPath)
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
            return redirect(f"itemListed/{item.pk}/")
    else:
        username, balance = getUsernameBalance(request)
        form = ItemForm()
    return render(request, "base/listAnItem.html", {"form": form, "username": username, "balance": balance,})
    
def itemListed(request, pk):
    username, balance = getUsernameBalance(request)
    item = get_object_or_404(Item, pk=pk)
    return render(request, "base/itemListed.html", {"item": item, "username": username, "balance": balance})
