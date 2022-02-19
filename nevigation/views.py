from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import LoginForm, RegisterForm
from django.contrib.auth.models import User
from store.models.user_profile import UserProfile
from store.models.cart import Cart, CartItem
from store.models.product import Product
import datetime
import dateutil.parser
import json
from django.contrib import messages
# from myapp.views import
# Create your views here.


def loginView(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': LoginForm})
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                response = redirect('products')

                if user:
                    login(request, user)
                    cart_cookie = request.COOKIES.get('cart')
                    cookie_update_time = request.COOKIES.get('cookie_update_time')
                    try:
                        if cart_cookie is not None:
                            print('cookie is not empty')
                            try:
                                cart_cookie = json.loads(cart_cookie)
                            except Exception as ex:
                                print('cookie load exeption----', ex)
                                messages.add_message(
                                    request, messages.ERROR, 'products cannot be added to cart')
                            print('print cookie data----', cart_cookie)
                            cart_instance = Cart.objects.filter(
                                user=request.user, status='D')
                            if len(cart_instance) == 0:
                                cart_instance = Cart.objects.create(
                                    user=user, created_at=datetime.datetime.now(), status='D')
                            elif len(cart_instance) != 1:
                                messages.add_message(
                                    request, messages.ERROR, 'multiple carts are availble,contact developer')
                                pass
                            else:
                                cart_instance = cart_instance[0]
                            cartItem_instance = CartItem.objects.filter(
                                cart=cart_instance)
                            if dateutil.parser.isoparse(cookie_update_time) > (cart_instance.updated_time).replace(tzinfo=None):
                                print('cookie data while syncing', cart_cookie)
                                for product, quantity in cart_cookie.items():
                                    cartItem_instance_product = cartItem_instance.filter(
                                        product__id=int(product))
                                    if len(cartItem_instance_product):
                                        cartItem_instance_product[0].quantity += int(
                                            quantity)
                                        cartItem_instance_product[0].save()
                                    else:
                                        product_instance = Product.objects.get(
                                            id=product)
                                        try:
                                            CartItem.objects.create(
                                                product=product_instance,
                                                quantity=int(quantity),
                                                price_ht=product_instance.price,
                                                cart=cart_instance,
                                            )
                                            cart_instance.updated_time = datetime.datetime.now()
                                            cart_instance.save()
                                        except Exception as ex:
                                            print(
                                                'cart model update exeption while syncing data----', ex)

                            print('-----------deleting cookies')
                            response.delete_cookie('cart')
                            response.delete_cookie('cookie_update_time')
                            return response
                    except Exception as ex:
                        print('cookie sync final exeption----', ex)
                        messages.add_message(
                            request, messages.ERROR, 'could not add products into cart, contact developer')
                    return response
                else:
                    return redirect('nevigate:Login')
            except Exception as ex:
                messages.add_message(
                            request, messages.ERROR, 'email or password are wrong')
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})


def registerView(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            print('registe form validated')
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            user_profile = UserProfile()
            user_profile.user = user
            user_profile.mobile = form.cleaned_data.get('mobile')
            try:
                user_profile.save()
            except:
                user.delete()
                form.add_error(
                    'mobile', 'could not register right now, try after sometime')
                return render(request, 'register.html', {'form': form})
            return redirect('nevigate:Login')
        else:
            return render(request, 'register.html', {'form': form})


def logoutView(request):
    try:
        logout(request)
        return redirect('nevigate:Login')
    except Exception as ex:
        print('logout exeption----', ex)
        return redirect('nevigate:Login')
