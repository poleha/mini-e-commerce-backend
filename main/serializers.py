from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from .models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount


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

