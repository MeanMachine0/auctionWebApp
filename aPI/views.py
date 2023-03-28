from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.models import User
from base.models import Accounts, Items, EndedItems
from .serializers import AccountsSerializer, UserSerializer, ItemsSerializer, EndedItemsSerializer, LoginSerializer
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate

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
    items = Items.objects.all()
    serializer = ItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getItem(request, pk):
    item = get_object_or_404(Items, pk=pk)
    serializer = ItemsSerializer(item)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getEndedItems(request):
    items = EndedItems.objects.all()
    serializer = EndedItemsSerializer(items, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def getEndedItem(request, pk):
    item = get_object_or_404(EndedItems, pk=pk)
    serializer = EndedItemsSerializer(item)
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