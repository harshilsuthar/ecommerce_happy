from django.urls import path
# from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cartitem', views.CartItemViewSet, basename='CartItem')
router.register(r'cart', views.CartViewSet, basename='Cart')

urlpatterns = [
    path("user/", views.UserRegisterViewset.as_view()),
    path("login/", views.UserAuthTokenViewSet.as_view()),
    path("product/", views.ProductViewSet.as_view()),
    path("product/<int:pk>/", views.ProductDetailsViewSet.as_view()),
]
urlpatterns += router.urls
