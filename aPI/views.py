from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.models import User
from base.models import Account, Item
from .serializers import AccountSerializer, UserSerializer, ItemSerializer, LoginSerializer
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate
from django.db.models.functions import Lower

toBool = {
    'true': True,
    'false': False,
}

categories = [
    'bOIS',
    'hB',
    'f',
    'e',
    'hG',
    'sHL',
    'mt',
    'cA',
    'mda',
    'o',
]

conditions = [
    'new',
    'excellent',
    'good',
    'used',
    'refurbished',
    'partsOnly',
]

sorters = [
    'price',
    'name',
    'endDateTime',
]

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                "userId": user.pk,
                "token": token.key,
                })
        return Response({'error': 'Invalid credentials'})

@api_view(["POST"])
def logout(request):
    token = request.META.get("HTTP_AUTHORIZATION").split(' ')[1]
    Token.objects.filter(key=token).delete()
    return Response({"message": "Logged out successfully."})

@api_view(["GET"])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getUser(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(["GET"])
def getAccounts(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getAccount(request, pk):
    account = get_object_or_404(Account, pk=pk)
    serializer = AccountSerializer(account)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getItems(request):
    sold = toBool[request.headers["sold"].lower()]
    ended = toBool[request.headers["ended"].lower()]
    searchBool = toBool[request.headers["searchBool"].lower()]
    search = request.headers["search"]
    category = request.headers["category"]
    condition = request.headers["condition"]
    sortBy = request.headers["sortBy"]
    ascending = toBool[request.headers["ascending"].lower()]
    items = Item.objects.filter(sold=True) if sold else Item.objects.filter(ended=ended)
    if searchBool:
        items = items.filter(name__icontains=search)
    if category in categories:
        items = items.filter(category=category)
    if condition in conditions:
        items = items.filter(condition=condition)
    if sortBy in sorters:
        if sortBy == 'name':
            items = items.order_by(Lower(sortBy)) if ascending else items.order_by("-" + Lower(sortBy))
        else: 
            items = items.order_by(sortBy) if ascending else items.order_by("-" + sortBy)
    for item in items:
        item.bidders = item.seller.user.username
        item.buyer = None
        if ended:
            item.destinationAddress = None
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getItem(request, pk):
    item = get_object_or_404(Item, pk=pk)
    seller = request.user.pk == item.seller_id
    if not seller:
        item.bidders = item.seller.user.username
        item.buyer = None
        item.destinationAddress = None
    serializer = ItemSerializer(item)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getAccountItems(request, pk):
    seller = request.user.pk == pk
    ended = toBool[request.headers['ended'].lower()]
    items = Item.objects.filter(Q(seller=pk) & Q(ended=ended))
    if seller:
        if len(items) < 2:
            item = get_object_or_404(items, seller=pk)
            serializer = ItemSerializer(item)
        else: 
            serializer = ItemSerializer(items, many=True)
    else: 
        if len(items) < 2:
            item = get_object_or_404(items, seller=pk)
            item.bidders = item.seller.user.username
            item.buyer = None
            if ended:
                item.destinationAddress = None
            serializer = ItemSerializer(item)
        else: 
            for item in items:
                item.bidders = item.seller.user.username
                item.buyer = None
                if ended:
                    item.destinationAddress = None
            serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def amITheBuyer(request, pk):
    accountId = request.user.pk
    if accountId is None:
        return Response({'IAmTheBuyer': False})
    item = Item.objects.get(pk=pk)
    IAmTheBuyer = item.buyer_id == accountId
    return Response({'IAmTheBuyer': IAmTheBuyer})

@api_view(["GET"])
def getItemsBidOnByMe(request, pk):
    accountId = request.user.pk
    if accountId != pk:
        return Response({'message': 'forbidden'})
    ended = toBool[request.headers['ended'].lower()]
    items = Item.objects.filter(ended=ended)
    items = items.exclude(bidders="[]")
    itemsBidOnByMe = []
    firstItemBidOnByMeId = 0
    for item in items:
        bidders = item.getBidders()
        if accountId in bidders:
            itemBuyerId = item.buyer_id
            if itemBuyerId != accountId:
                item.buyer = None
                if ended:
                    item.destinationAddress = None
            item.bidders = item.seller.user.username
            itemsBidOnByMe.append(item)
            if len(itemsBidOnByMe) == 1:
                firstItemBidOnByMeId = item.pk
    if len(itemsBidOnByMe) < 2:
            itemBidOnByMe = get_object_or_404(Item, pk=firstItemBidOnByMeId)
            itemBuyerId = itemBidOnByMe.buyer_id
            if itemBuyerId != accountId:
                itemBidOnByMe.buyer = None
                if ended:
                    itemBidOnByMe.destinationAddress = None
            itemBidOnByMe.bidders = itemBidOnByMe.seller.user.username
            serializer = ItemSerializer(itemBidOnByMe)
    else: 
        serializer = ItemSerializer(itemsBidOnByMe, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def createUser(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
def createItem(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        if (serializer.validated_data['seller'].id == request.user.pk and 
        serializer.validated_data['endDateTime'] > timezone.now() and 
        serializer.validated_data['endDateTime'] <= timezone.now() + timedelta(days=30)):
            serializer.save()
        elif serializer.validated_data['seller'].id != request.user.pk:
            return Response({'error': 'Invalid credentials.'})
        else:
            return Response({'error': 'End Date/Time must be within 30 days from now.'})
    else:
        return Response({'error': 'Invalid item.'})
    return Response({'itemId': serializer.data['id']})

@api_view(["POST"])
def submitBid(request, pk):
    accountId = request.data['accountId']
    bid = float(request.data['bid'])
    item = get_object_or_404(Item, pk=pk)
    bidIncrement = float(item.bidIncrement)
    minBid = float(item.price) + bidIncrement
    postageCost = float(item.postageCost)
    totalCost = bid + bidIncrement + postageCost
    balance = float(Account.objects.get(pk=accountId).balance)
    if bid >= minBid and balance >= totalCost and accountId != item.seller_id and timezone.now() < item.endDateTime:
        item.price = bid
        item.numBids += 1
        item.buyer = Account.objects.get(user__pk=request.user.pk)
        bidders = item.getBidders()
        bidders.append(accountId)
        item.setBidders(bidders)
        item.save()
    item = get_object_or_404(Item, pk=pk)
    serializer = ItemSerializer(item)
    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delUser(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserSerializer(user)
    user.delete()
    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delItem(request, pk):
    item = get_object_or_404(Item, pk=pk)
    serializer = ItemSerializer(item)
    item.delete()
    return Response(serializer.data)

@api_view(["POST"])
def setFcmToken(request):
    fcmToken = request.body.decode("utf-8")
    account = Account.objects.get(pk=request.user.pk)
    account.fcmToken = fcmToken
    account.save()
    return Response({'fcmToken': fcmToken})
