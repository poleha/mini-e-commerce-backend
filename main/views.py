from rest_framework import filters
from main.models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount
from main.serializers import ProductSerializer, ProductInCartSerializer,\
    UserProfileSerializer, VendorProfileSerializer, SocialAccountSerializer
from .filters import ProductFilter
from django.utils.timezone import now
from .permissions import OwnerOnlyPermission, VendorOnlyPermission, OwnerOrReadOnlyPermission

from rest_framework import viewsets, mixins


class BaseProductViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProductFilter


class ProductUserViewSet(BaseProductViewSet):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(expire_date__gt=now())


class ProductVendorViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, BaseProductViewSet):
    permission_classes = (OwnerOnlyPermission, VendorOnlyPermission)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)



class ProductInCartViewSet(viewsets.ModelViewSet):
    queryset = ProductInCart.objects.all()
    serializer_class = ProductInCartSerializer
    permission_classes = (OwnerOnlyPermission,)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class VendorProfileViewSet(viewsets.ModelViewSet):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = (OwnerOrReadOnlyPermission, )


class SocialAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialAccount.objects.all()
    serializer_class = SocialAccountSerializer
    permission_classes = (OwnerOrReadOnlyPermission,)