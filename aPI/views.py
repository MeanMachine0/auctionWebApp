from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from base.models import Accounts, Items, EndedItems
from .serializers import AccountsSerializer, UserSerializer, ItemsSerializer, EndedItemsSerializer
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate, login, logout

@api_view(["POST"])
@permission_classes([AllowAny])
def loginView(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if user is not None:
            login(request, user)
    return Response(serializer.data)

class GetIdToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={"request": request})
        if serializer.is_valid():
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is not None:
                login(request, user)
                user = serializer.validated_data["user"]
                token, created = Token.objects.get_or_create(user=user)
        return Response({
            "userId": user.pk,
            "token": token.key,
        })

@api_view(["GET"])
def logoutView(request):
    logout(request)
    return Response(None)

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