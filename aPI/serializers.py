from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import Accounts, Items, EndedItems

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = "__all__"

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = "__all__"

class EndedItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndedItems
        fields = "__all__"