from rest_framework import serializers
from .models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

class ProductInCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInCart

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile


class VendorProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorProfile


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
