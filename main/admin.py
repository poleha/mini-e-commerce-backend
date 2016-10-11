from django.contrib import admin
from . import models


@admin.register(models.VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ProductInCart)
class ProductInCartAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    pass