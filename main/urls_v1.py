from django.conf.urls import url, include
from main import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'products_in_cart', views.ProductInCartViewSet)
router.register(r'user_profiles', views.UserProfileViewSet)
router.register(r'vendor_profiles', views.VendorProfileViewSet)
router.register(r'social_accounts', views.SocialAccountViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]