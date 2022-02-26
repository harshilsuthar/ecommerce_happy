
from django.contrib import admin
from django.urls import path

from .views.home import *
from .views.cartview import *
from .views.orderview import reOrder, buyAgain
from .views.reviewview import ReviewView, rating
from .views.userview import UserProfileView,changePasswordView,setDefaultAddress
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('products/', Products.as_view(), name='products'),
    path('get_product_quantity',getCurrentProductQuantity, name='GetProductQuantity'),
    
    path('product_detail_view/',product_detail_view, kwargs={'':''} ,name='product_detail_view'),
    path('product/<int:id>/', product_detail_view, name='product_detail_view'),
    path("cart/", cartIndex, name="CartIndex"),
    path("addToCart/", addToCart, name="addToCart"),
    path("wishlist/", WishListView.as_view(), name="Wishlist"),
    path("removeWishlist/", removeWishlist, name="RemoveWishlist"),
    path("changecartquantity/<int:product_id>/<int:quantity>/", ChangeCartQuantity.as_view(), name="ChangeCartQuantity"),
    path("removeproduct/<int:product_id>/", RemoveProduct.as_view(), name="RemoveProduct"),
    path("checkout/", Checkout.as_view(), name="Checkout"),
    path("payment/", paymentPage, name="PaymentPage"),

    # payment gateways
    path("authorizePaymentGateway/", authorizePaymentGateway, name="AuthorizePaymentGateway"),
    path("stripe_payment/", stripe_payment, name="StripePayment"),
    
    path("remove_address/<int:address_id>", removeAddress, name="RemoveAddress"),
    path("add_address/", addAddress, name="AddAddress"),
    path("edit_address/<int:address_id>/", edit_address, name="EditAddress"),
    path('set_default_address/<int:address_id>',setDefaultAddress,name='SetDefaultAddress'),

    path("change_state/", changeState, name="ChangeState"),
    path("change_city/", changeCity, name="ChangeCity"),
    path('payment_success/',paymentSuccess, name='PaymentSuccess'),
    path("stripePaymentOrderHandler/", stripePaymentOrderHandler, name="StripePaymentOrderHandler"),
    path('payment_fail/',paymentFail, name='paymentFail'),
    # path("orders/", OrderView.as_view(), name="OrderView"), 
    path("reorder/<int:order_id>", reOrder, name="ReOrder"),
    path("buy_again/<int:product_id>", buyAgain, name="BuyAgain"),
    path("review/", ReviewView.as_view(), name="Review"),
    path("rating/", rating, name="Rating"),
    path("userprofile/", UserProfileView.as_view(), name="UserProfileView"),
    path("change_password/", changePasswordView, name="ChangePasswordView"),
    
    path('change_product_tag_m2m_admin/', update_product_tag_admin, name='UpdateProdcutTagAdmin'),
    path('change_product_attribute_m2m_admin/', update_product_attribute_admin, name='UpdateProductAttributeAdmin'),
    path('update_product_attribute_name_list/',update_product_attribute_name_list,name='UpdateProductAttributeNameList'),
    path("update_product_tag_name_list/", update_product_tag_name_list, name="UpdateProductTagNameList")
]
