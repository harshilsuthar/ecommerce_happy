# django imports
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

# app imports 
from store.models.order import Order
from store.models.product import Product
from store.models.cart import Cart, CartItem


@login_required
def reOrder(request, order_id):
    if request.method == 'GET':
        try:
            order_instance = Order.objects.get(id=order_id)
            try:
                cart_instance = Cart.objects.get(status='D', user=request.user)
            
            except MultipleObjectsReturned as mor:
                print(mor)
                Cart.objects.filter(status='D', user=request.user).delete()
                cart_instance = Cart.objects.create(user= request.user, status='D')
            except ObjectDoesNotExist:
                print('new cart object creating from orderview for reorder-------exception handled')
                cart_instance = Cart.objects.create(user= request.user, status='D')
            cartitem_instance = cart_instance.cartitem_set.all()
            cart_instance.cartitem_set.all().delete()
            for cart_item in order_instance.cart.cartitem_set.all():
                CartItem.objects.create(cart=cart_instance, product=cart_item.product, quantity=cart_item.quantity, price_ht=cart_item.product.price)
        except Exception as ex:
            print(ex)
        finally:
            return redirect('Checkout')

def buyAgain(request, product_id):
    if request.method == 'GET':
        try:
            product = Product.objects.get(id = product_id)
            try:
                cart_instance = Cart.objects.get(status='D', user=request.user)
            except MultipleObjectsReturned as mor:
                print(mor)
                Cart.objects.filter(status='D', user=request.user).delete()
                cart_instance = Cart.objects.create(user= request.user, status='D')
            except ObjectDoesNotExist:
                print('new cart object creating from orderview for reorder-------exception handled')
                cart_instance = Cart.objects.create(user= request.user, status='D')
            cartitem_instance = cart_instance.cartitem_set.all()
            cart_instance.cartitem_set.all().delete()
            CartItem.objects.create(cart=cart_instance, product=product, quantity=1, price_ht=product.price)
        except Exception as ex:
            print(ex)
        finally:
            return redirect('Checkout')