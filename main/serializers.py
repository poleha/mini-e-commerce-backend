from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from .models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount, User, ACCOUNT_TYPE_VENDOR
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

def validate_user(self, value):
    user = self.context['request'].user
    if user != value:
        raise serializers.ValidationError(_("Unable to alter another user's object."))
    return value

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

    validate_user = validate_user

class ProductInCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInCart

    validate_user = validate_user



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile

    validate_user = validate_user


class VendorProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorProfile

    validate_user = validate_user


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    retype_password = serializers.CharField(write_only=True)
    account_type = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(validators=[
        UniqueValidator(queryset=User.objects.all()),
    ]
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'retype_password', 'account_type', 'email')

    def create(self, validated_data):
        with transaction.atomic():
            account_type = validated_data.pop('account_type')

            user = User.objects.create_user(**validated_data)
            Token.objects.get_or_create(user=user)
            user_profile = UserProfile(user=user, account_type = account_type)
            user_profile.save()

            if account_type == ACCOUNT_TYPE_VENDOR:
                VendorProfile.objects.get_or_create(user=user)
        return user

    def validate(self, data):
        retype_password = data.pop('retype_password')
        if data['password'] != retype_password:
            raise serializers.ValidationError(_("Passwords not equal."))
        return data


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token

class SocialLoginSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    network = serializers.CharField()
    email = serializers.EmailField(required=False)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')