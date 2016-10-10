from rest_framework import filters
from main.models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount
from main.serializers import ProductSerializer, ProductInCartSerializer,\
    UserProfileSerializer, VendorProfileSerializer, SocialAccountSerializer
from .filters import ProductFilter
from django.utils.timezone import now
from .permissions import OwnerOnlyPermission, VendorOnlyPermission, OwnerOrReadOnlyPermission
from rest_framework import status, views, viewsets, mixins
from rest_framework.response import Response
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import transaction


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


class CartView(views.APIView):
    subject_template_name = 'main/purchase_email_subject.txt'
    plain_body_template_name = 'main/purchase_email_body.txt'
    html_body_template_name = 'main/purchase_email_body.html'

    def send_email(self, to_email, from_email, context):
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        plain_body = loader.render_to_string(self.plain_body_template_name, context)
        email_message = EmailMultiAlternatives(subject, plain_body, from_email, [to_email])

        html_body = loader.render_to_string(self.html_body_template_name, context)
        email_message.attach_alternative(html_body, 'text/html')

        email_message.send()

    def get_email_context(self, carts):
        return {
            'carts': carts,
            'site_name': settings.SITE_NAME
        }

    def get_carts(self, user):
        return ProductInCart.objects.filter(user=user, purchased=False)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        user = request.user
        carts = self.get_carts(user)
        if user.is_authenticated() and carts.exists():
            for cart in carts:
                cart.purchased = True
                cart.purchase_time = now()
                cart.save()
            self.send_email(user.email, settings.DEFAULT_FROM_EMAIL, self.get_email_context(carts))
            serializer = ProductInCartSerializer(carts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


    def get(self, request, *args, **kwargs):
        user = request.user
        carts = self.get_carts(user)
        serializer = ProductInCartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)