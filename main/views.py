from rest_framework import filters
from main.models import Product, ProductInCart, UserProfile, VendorProfile, SocialAccount
from main.serializers import ProductSerializer, ProductInCartSerializer,\
    UserProfileSerializer, VendorProfileSerializer, SocialAccountSerializer,\
    RegistrationSerializer, TokenSerializer, SocialLoginSerializer, UserSerializer
from .filters import ProductFilter
from django.utils.timezone import now
from .permissions import OwnerOnlyPermission, VendorOnlyPermission, OwnerOrReadOnlyPermission
from rest_framework import status, views, viewsets, mixins, generics
from rest_framework.response import Response
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _

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

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data.get('product')
        if user.is_authenticated() and not product.is_expired() and \
                not ProductInCart.objects.filter(product=product, user=user, purchased=False).exists():
            serializer.save(user=user)
        else:
            raise ValidationError(_('Unable to add product to cart'))




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
    def delete(self, request):
        user = request.user
        product_pk = request.data.get('product')
        ProductInCart.objects.filter(user=user, product_id=product_pk, purchased=False).delete()
        queryset = ProductInCart.objects.filter(user=user, purchased=False)
        serializer = ProductInCartSerializer(queryset, many=True)
        return Response(
            {
            'results': serializer.data,
            'count': queryset.count()
            }
        )

    @transaction.atomic()
    def post(self, request):
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


    def get(self, request):
        user = request.user
        carts = self.get_carts(user)
        serializer = ProductInCartSerializer(carts, many=True)
        return Response({
            'results': serializer.data,
            'count': carts.count()
        },
            status=status.HTTP_200_OK)


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer



class SocialLoginView(views.APIView):

    # TODO change to normal validation
    def login_user(self, data):
        user_id = data['user_id']
        network = data['network']
        email = data['email']
        username = data['username']

        users_by_id = User.objects.filter(social_accounts__external_id=user_id, social_accounts__network=network)
        users_by_email_exists = False
        users_by_email = None
        if email:
            users_by_email = User.objects.filter(email=email)
            users_by_email_exists = users_by_email.exists()

        user = None

        if users_by_id.exists() and email and users_by_email_exists and users_by_id[0].pk != users_by_email[0].pk:
            raise ValidationError(_('This email is used by another user'))
        elif users_by_id.exists():
            user = users_by_id[0]
        elif users_by_email_exists:
            user = users_by_email[0]

        if not user:
            users_by_username = User.objects.filter(username=username)
            k = 0
            while users_by_username.exists():
                k += 1
                username += str(k)
                users_by_username = User.objects.filter(username=username)
            user = User.objects.create(username=username)

        social_account, created = SocialAccount.objects.get_or_create(user=user, network=network)
        social_account.external_id = id
        social_account.save()

        user_profile, created = UserProfile.objects.get_or_create(user=user)

        token, created = Token.objects.get_or_create(user=user)
        return Response(
            data=TokenSerializer(token).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        if serializer.is_valid():
            return self.login_user(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class GetUserInfo(views.APIView):

    def get(self, request):
        user = request.user
        if not user.is_authenticated():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        token_serializer = TokenSerializer(user.auth_token)
        user_serializer = UserSerializer(user)
        user_profile_serializer = UserProfileSerializer(user.user_profile)
        #TODO fix
        vendor_profile, created = VendorProfile.objects.get_or_create(user=user)
        vendor_profile_serializer = VendorProfileSerializer(vendor_profile)

        return Response({
           'user': user_serializer.data,
            'token': token_serializer.data,
            'user_profile': user_profile_serializer.data,
            'vendor_profile': vendor_profile_serializer.data,
        })