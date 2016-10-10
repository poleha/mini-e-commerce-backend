from django.db import models
from django.contrib.auth.models import AnonymousUser, User
from django.utils.translation import ugettext_lazy as _

FACEBOOK = 'facebook'

SOCIAL_NETWORKS = (
    (FACEBOOK, FACEBOOK),
)

ACCOUNT_TYPE_VENDOR = 1
ACCOUNT_TYPE_CUSTOMER = 2

ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_VENDOR, _('Vendor')),
    (ACCOUNT_TYPE_CUSTOMER, _('Customer')),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    account_type = models.PositiveIntegerField(choices=ACCOUNT_TYPES, verbose_name=_('Account type'))
    email_confirmed = models.BooleanField(default=False)
    receive_email_notifications = models.BooleanField(default=True)

class VendorProfile(models.Model):
    user = models.OneToOneField(User, related_name='vendor_profile')
    business_name = models.CharField(max_length=3000)
    location = models.CharField(max_length=3000)
    description = models.TextField()


class SocialAccount(models.Model):
    user = models.ForeignKey(User, related_name='social_accounts')
    external_id = models.CharField(max_length=500, null=True, blank=True)
    network = models.CharField(choices=SOCIAL_NETWORKS, max_length=20)


class Product(models.Model):
    class Meta:
        ordering = ['-created']

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='products')
    title = models.CharField(max_length=1000)
    body = models.TextField(null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name=_('Price'))
    expire_date = models.DateTimeField(verbose_name=_('Expire date'))


class ProductInCart(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, related_name='carts')
    user = models.ForeignKey(User)
    purchased = models.BooleanField(default=False, blank=True)
    purchase_time = models.DateTimeField(null=True, blank=True)

User.is_vendor = lambda self: self.user_profile.account_type == ACCOUNT_TYPE_VENDOR
AnonymousUser.is_vendor = lambda self: False
