from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import Account, Item

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Account
        fields = "__all__"

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
