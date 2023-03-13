from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from hello.models import Accounts, Items, EndedItems
from .serializers import AccountsSerializer, UserSerializer, ItemsSerializer, EndedItemsSerializer
from django.shortcuts import get_object_or_404 

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
def getItems(request):
    items = Items.objects.all()
    serializer = ItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getItem(request, pk):
    item = get_object_or_404(Items, pk=pk)
    serializer = ItemsSerializer(item)
    return Response(serializer.data)

@api_view(["GET"])
def getEndedItems(request):
    items = EndedItems.objects.all()
    serializer = EndedItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def getEndedItem(request, pk):
    item = get_object_or_404(EndedItems, pk=pk)
    serializer = EndedItemsSerializer(item)
    return Response(serializer.data)

@api_view(["POST"])
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
    return Response(serializer.data)

@api_view(["DELETE"])
def delUser(request, pk):
    user = get_object_or_404(User, pk=pk)
    serializer = UserSerializer(user)
    user.delete()
    return Response(serializer.data)

@api_view(["DELETE"])
def delItem(request, pk):
    item = get_object_or_404(Items, pk=pk)
    serializer = ItemsSerializer(item)
    item.delete()
    return Response(serializer.data)