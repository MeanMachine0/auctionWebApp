from django.utils import timezone
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.models import User
from base.models import Accounts, Items
from .serializers import AccountsSerializer, UserSerializer, ItemsSerializer, LoginSerializer
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate

toBool = {
    'true': True,
    'false': False,
}

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
    accounts = Accounts.objects.all()
    serializer = AccountsSerializer(accounts, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getAccount(request, pk):
    account = get_object_or_404(Accounts, pk=pk)
    serializer = AccountsSerializer(account)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getItems(request):
    sold = toBool[request.headers["sold"].lower()]
    ended = toBool[request.headers["ended"].lower()]
    items = Items.objects.filter(sold=True) if sold else Items.objects.filter(ended=ended)
    for item in items:
        item.bidders = '[]'
        item.buyer = None
    serializer = ItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getItem(request, pk):
    item = get_object_or_404(Items, pk=pk)
    seller = request.user.pk == item.seller_id
    if not seller:
        item.bidders = '[]'
        item.buyer = None
        item.destinationAddress = None
    serializer = ItemsSerializer(item)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getAccountItems(request, pk):
    seller = request.user.pk == pk
    ended = toBool[request.headers['ended'].lower()]
    items = Items.objects.filter(Q(seller=pk) & Q(ended=ended))
    if seller:
        if len(items) < 2:
            item = get_object_or_404(items, seller=pk)
            serializer = ItemsSerializer(item)
        else: 
            serializer = ItemsSerializer(items, many=True)
    else: 
        if len(items) < 2:
            item = get_object_or_404(items, seller=pk)
            item.bidders = '[]'
            item.buyer = None
            if ended:
                item.destinationAddress = None
            serializer = ItemsSerializer(item)
        else: 
            for item in items:
                item.bidders = '[]'
                item.buyer = None
                if ended:
                    item.destinationAddress = None
            serializer = ItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def amITheBuyer(request, pk):
    accountId = request.user.pk
    if accountId is None:
        return Response({'IAmTheBuyer': False})
    item = Items.objects.get(pk=pk)
    IAmTheBuyer = item.buyer_id == accountId
    return Response({'IAmTheBuyer': IAmTheBuyer})

@api_view(["GET"])
def getItemsBidOnByMe(request, pk):
    accountId = request.user.pk
    if accountId != pk:
        return Response(None)
    ended = toBool[request.headers['ended'].lower()]
    items = Items.objects.filter(ended=ended)
    items = items.exclude(bidders="[]")
    itemsBidOnByMe = []
    firstItemBidOnByMeId = 0
    for item in items:
        bidders = item.getBidders()
        if accountId in bidders:
            itemBuyerId = item.buyer_id
            if itemBuyerId != accountId:
                item.bidders = '[]'
                item.buyer = None
                if ended:
                    item.destinationAddress = None
            itemsBidOnByMe.append(item)
            if len(itemsBidOnByMe) == 1:
                firstItemBidOnByMeId = item.pk
    if len(itemsBidOnByMe) < 2:
            itemBidOnByMe = get_object_or_404(Items, pk=firstItemBidOnByMeId)
            serializer = ItemsSerializer(itemBidOnByMe)
    else: 
        serializer = ItemsSerializer(itemsBidOnByMe, many=True)
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
    serializer = ItemsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response({'itemId': serializer.data['id']})

@api_view(["POST"])
def submitBid(request, pk):
    accountId = request.data['accountId']
    bid = float(request.data['bid'])
    item = get_object_or_404(Items, pk=pk)
    bidIncrement = float(item.bidIncrement)
    minBid = float(item.price) + bidIncrement
    postageCost = float(item.postageCost)
    totalCost = bid + bidIncrement + postageCost
    balance = float(Accounts.objects.get(pk=accountId).balance)
    if bid >= minBid and balance >= totalCost and accountId != item.seller_id and timezone.now() < item.endDateTime:
        item.price = bid
        item.numBids += 1
        item.buyer = Accounts.objects.get(user__pk=request.user.pk)
        bidders = item.getBidders()
        bidders.append(accountId)
        item.setBidders(bidders)
        item.save()
    item = get_object_or_404(Items, pk=pk)
    serializer = ItemsSerializer(item)
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
    item = get_object_or_404(Items, pk=pk)
    serializer = ItemsSerializer(item)
    item.delete()
    return Response(serializer.data)