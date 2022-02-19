from .models.cart import Cart, CartItem
from .models.category import Category
import json
from django.db.models import Sum, F, DecimalField
from django.shortcuts import HttpResponse


def cart_count(request):
    try:
        cart_count_value = 0
        if request.user.is_authenticated:
            cart_instance = Cart.objects.filter(user=request.user, status='D')
            if len(cart_instance) == 1:
                cart_instance = cart_instance[0]
                cart_count_value = CartItem.objects.filter(
                    cart=cart_instance).aggregate(Sum('quantity'))
                cart_count_value = cart_count_value['quantity__sum']
                # print('*-*-*-',cart_count_value)
            else:
                cart_count_value = 0
        else:
            try:
                cart_cookie = request.COOKIES.get('cart')
                if cart_cookie != None:
                    cart_cookie = json.loads(cart_cookie)
                    cart_count_value = sum(map(int, cart_cookie.values()))
                    # cart_count_value = len(cart_cookie)
                else:
                    cart_count_value = 0
            except Exception as ex:
                cart_count_value = 0
        # print('******',int(cart_count_value))
        return {'cart_count': int(cart_count_value)}
    except Exception as ex:
        return {'cart_count': 0}


def cart_total_amount(request):
    try:
        cart_count_value = 0
        if request.user.is_authenticated:
            cart_instance = Cart.objects.filter(user=request.user, status='D')
            if len(cart_instance) == 1:
                cart_instance = cart_instance[0]
                cart_count_value = CartItem.objects.filter(cart=cart_instance).aggregate(
                    total=Sum(F('quantity')*F('price_ht'), output_field=DecimalField(decimal_places=2,max_digits=10)))
                # print('---------',cart_count_value)
                return {'cart_total_amount': cart_count_value['total']}
            else:
                return {'cart_total_amount': 0}
        else:
            return {'cart_total_amount': 0}
    except Exception as ex:
        print('final exeption cart_total_amount----', ex)
        return {'cart_total_amount': 0}


def showMenuCart(request):
    try:
        cart_instance = Cart.objects.get(user=request.user, status='D')
        cartitem_instance  = CartItem.objects.filter(cart=cart_instance)
    except Exception as ex:
        print('cart in menu exception----error')
        print(ex)
        cartitem_instance = CartItem.objects.none()
    finally:
        return {'cartitem_instance':cartitem_instance}


def navCategories(request):
    try:
        categories = Category.get_annotated_list()
    except Exception as ex:
        categories = []
        print('loding categories exception in context processor---error')
        print(ex)
    return {'nav_categories':categories}

# def ratingHTML(request,product_id):
#     text = ''
#     product = Product.objects.get(id=int(product_id))
#     rating = ProductReview.average_rating(product)['review_rating__avg']
#     users = ProductReview.user_count(product)
#     for i in range(1,6):
#         if i<rating and i!= int(rating):
#             text += '<i class="fas fa-star" style="color:#FFCC36"></i>'
#         elif i == rating:
#             text += '<i class="fas fa-star" style="color:#FFCC36"></i>'
#         elif i < rating and i == int(rating):
#             text += '<i class="fas fa-star-half-alt" style="color:#FFCC36"></i>'
#         else:
#             text += '<i class="far fa-star" style="color:#FFCC36"></i>' 
#     return {'ratingHTML':HttpResponse(text)}