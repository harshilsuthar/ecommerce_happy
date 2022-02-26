# response handlers
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse

# from store app
from store.models.cart import Cart, CartItem, Wishlist
from store.models.product import Product, Category
from store.models.address import State, City, UserAddress, Country
from store.models.order import Order
from store.forms import CheckOutForm, PaymentForm, AddressForm, PaymentAddressForm


# for security
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# for messages supply
from django.contrib import messages


# payment gateway
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
import stripe

# sending mail and html format
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# send email via thread
import threading
from threading import Thread

# for creating query
from django.db.models import Q

# other important
from django.views import View
import traceback
import datetime
import json

def cartIndex(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            try:
                # return main cart which is in draft phase
                cart_data = Cart.objects.get(user=request.user, status='D')
                return render(request, 'cart.html',{'cart_data':cart_data})
            except Exception as ex:
                traceback.print_exc()
                print('exeption in load cart----',ex)
                return render(request, 'cart.html')


        # returning cart data from cookies
        else:
            
            print('user is not authenticated...........')
            cart_cookie = request.COOKIES.get('cart')

            if (cart_cookie == None or not cart_cookie):
                return render(request, 'cart.html')
            else:
                cart_cookie = json.loads(cart_cookie)
                products = Product.objects.filter(id__in=cart_cookie.keys()).exclude(parent=None)

                print(cart_cookie,'-----------cart cookie data')
                return render(request, 'cart.html',{'cart_cookie':cart_cookie,'products':products})
                


def updateCookie(request ,product, quantity, response, update_type):
    try:
        try:
            product = Product.objects.get(id=product)
            # if add to cart from products page then first varient will be added
            if product.parent == None:
                product = Product.get_first_child(product).id
            else:
                product = product.id
        except Exception as ex:
            print(ex,'-------------------ex in cartview add to cart')
        if quantity == None or quantity == '':
            set_quantity = 1
        else:
            set_quantity = int(quantity)

        current_date_time = datetime.datetime.now().isoformat()
        
        if not request.user.is_authenticated:
            cart_cookie = request.COOKIES.get('cart')
            print('cookie data before add cart')
            print('cookie from system----', cart_cookie)
            
            # if cookie is not set or not available then create new one
            if (cart_cookie == None or not cart_cookie):
                cart_value = {"%s" % (product): "%s" % (str(set_quantity))}
                response.set_cookie('cart', json.dumps(cart_value))
                response.set_cookie('cookie_update_time',
                                    str(current_date_time))

            # updating cookie data
            else:
                cart_cookie = json.loads(cart_cookie)
                if cart_cookie.get('%s' % (product)):
                    if update_type == 'increasing':
                        cart_cookie['%s' % (product)] = str(
                            int(cart_cookie['%s' % (product)])+set_quantity)
                    elif update_type == 'updating':
                        if set_quantity >= 1: 
                            cart_cookie['%s' % (product)] = str(set_quantity)
                        else:
                            cart_cookie.pop('%s' % (product))
                else:
                    cart_cookie['%s' % (product)] = str(set_quantity)
                
                response.set_cookie('cart', json.dumps(cart_cookie))
                response.set_cookie('cookie_update_time',
                                    str(current_date_time))
        return response

        # if user is logged in then add product to cart and will change database
    except Exception as ex:
        print(ex)
        return HttpResponse(0)


@method_decorator(csrf_exempt, name='dispatch')
class WishListView(LoginRequiredMixin,View):

    # returning all wishlist data 
    def get(self, request, *args, **kwargs):
        try:
            wishlists = Wishlist.objects.filter(user=request.user)
            return render(request, 'wishlist.html', {'wishlists':wishlists})
        except Exception as ex:
            print(ex)
            return HttpResponse('page not found')
    
    # return ajax response for product add to wishlist
    
    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            product = Product.objects.get(id=int(product_id))
            if product.parent == None:
                product = Product.get_first_child(product)
            wishlist = Wishlist.objects.filter(user=request.user, product=product)
            # if no product in wishlist then create new record in it
            if len(wishlist) == 0:
                Wishlist.objects.create(user=request.user, product=product)

            # if same product occures multipletime in wishlist then delete other products and save 1 product from it
            elif len(wishlist) > 1:
                wishlist[:1].delete()
            return HttpResponse('product added to wishlist')
        except Exception as ex:
            print(ex)
            return HttpResponse('could not add to wishlist')

@csrf_exempt
def removeWishlist(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            product = Product.objects.get(id=int(product_id))
            if product.parent == None:
                product = Product.get_first_child(product)
            wishlist = Wishlist.objects.get(user=request.user, product=product)
            wishlist.delete()
            return HttpResponse('product removed from wishlist')
        except Exception as ex:
            print(ex)
            return HttpResponse('could not remove from wishlist')


def addToCart(request):
    if request.method == 'GET':
        quantity = request.GET.get('quantity')
        product_id = request.GET.get('product_id')
        redirect_page = request.GET.get('redirect_page')
        
        if not request.user.is_authenticated:
            response = updateCookie(request, product_id, quantity, HttpResponse(1), 'increasing')
        else:
            try:
                product = Product.objects.get(id=int(product_id))
                if product.parent == None:
                    product = Product.get_first_child(product)
                
                q = Q()
                all_unavailabel_categories_path_list = [category.path for category in Category.objects.filter(available=False)]
                for unavailable in all_unavailabel_categories_path_list:
                    q|= Q(path__startswith = unavailable)
                all_available_categories = Category.objects.all().exclude(q|Q(path__in=all_unavailabel_categories_path_list))
                products = Product.objects.filter(is_published=True,category__in=all_available_categories)
                if product not in products:
                    raise Exception('Product Is Not Available')
                if quantity == None or quantity == '' or quantity == 0:
                    set_quantity = 1
                else:
                    set_quantity = int(quantity)
                
                cart_instance = Cart.objects.filter(user=request.user, status='D')
                if len(cart_instance) == 1:
                    cart_instance = cart_instance[0]
                    cartitem_instance = CartItem.objects.filter(cart=cart_instance, product=product)
                    try:
                        # if product is adding first time then create cartitem
                        if len(cartitem_instance) == 0:
                            product_instance = product
                            CartItem.objects.create(
                                product = product_instance,
                                quantity = set_quantity,
                                price_ht = product_instance.price,
                                cart = cart_instance,
                            )
                        
                        # if product is already present in then increase product quantity
                        elif len(cartitem_instance)  == 1:
                            cartitem_instance = cartitem_instance[0]
                            cartitem_instance.quantity += set_quantity
                            cartitem_instance.save()
                            cart_instance.updated_time = datetime.datetime.now()
                            cart_instance.save()

                    except Exception as ex:
                        print('add product click creating or increase cart quantity exeption----error')
                        traceback.print_exc()
                        print(ex)
                
                # if cart does not exist then create new one and add product to cart
                elif len(cart_instance) == 0:
                    cart_instance = Cart.objects.create(
                        user=request.user,
                        created_at = datetime.datetime.now(),
                        status='D'
                    )

                    CartItem.objects.create(
                        product = product,
                        quantity = 1 ,
                        price_ht = product.price,
                        cart = cart_instance,
                    )

                return HttpResponse(1)
            except Exception as ex:
                traceback.print_exc()
                return HttpResponse(0)
        return response


class ChangeCartQuantity(View):
    def get(self, request, product_id, quantity):
        if request.user.is_authenticated:
            try:
                cart_instance = Cart.objects.get(user=request.user, status='D')
                cartitem_instance = CartItem.objects.get(cart=cart_instance, product__id=product_id)

                # if quantity set 0 then delete from cartitems
                if quantity == 0 or quantity == None:
                    message = '%s product deleted'%(cartitem_instance.product.name)
                    cartitem_instance.delete()
                

                # else update cart product quantity
                else:
                    cartitem_instance.quantity = quantity
                    cartitem_instance.save()
                response = 'product quantity updated'
            except Exception as ex:
                print('change cart quantity exception----error')
                print(ex)
                response = 'Could not update cart quantity, contact developer'
            finally:
                return HttpResponse(response)
        else:
            response = updateCookie(request,product_id,quantity,HttpResponse(1),'updating')
            if response == HttpResponse(1):
                response.content = 'product quantity updated'
            else:
                response.content = 'Could not update cart quantity, contact developer'
            return response


class RemoveProduct(View):
    def get(self,request, product_id):
        if request.user.is_authenticated:
            try:
                cart_instance = Cart.objects.get(user=request.user, status='D')
                CartItem.objects.get(cart=cart_instance, product__id=product_id).delete()
                return redirect('CartIndex')
            except Exception as ex:
                print('remove product from cart exception----error')
                print(ex)
                return redirect('CartIndex')
        else:
            try:
                response = updateCookie(request ,product_id, 0, redirect('CartIndex'), 'updating')
                if response.content == redirect('CartIndex').content:
                   return response
                else:
                    response = redirect('CartIndex')
            except Exception as ex:
                print(ex,'-------exception while removing product from cookie')
                response = redirect('CartIndex')
            finally:
                return response
       
@login_required
def removeAddress(request, address_id):
    if request.method == 'GET':
        try:
            # if this address is not used in placing order then remove it
            useraddress_instance = get_object_or_404(UserAddress, id=address_id)
            if Order.objects.filter(Q(address=useraddress_instance)|Q(shipping_address=useraddress_instance)).count() == 0:
                useraddress_instance.delete()

            # if address is used in order then make it unavailable
            else:
                useraddress_instance.available = False
                useraddress_instance.save()
            return HttpResponse('deleted')
        except Exception as ex:
            print(ex)
            return HttpResponse('could not delete')


def changeState(request):
    country_id = request.GET.get('country_id')
    try:
        option_list = State.objects.filter(country__id = country_id)
    except Exception:
        option_list = []
    return render(request, 'select_options.html', {'option_list':option_list, 'default':'Select State'})


def changeCity(request):
    state_id = request.GET.get('state_id')
    try:
        option_list = City.objects.filter(state__id = state_id)
    except Exception:
        option_list = []
    return render(request, 'select_options.html', {'option_list':option_list, 'default':'Select City'})


class Checkout(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        try:
            payment_form = PaymentAddressForm()
            cart_instance = Cart.objects.get(user=request.user, status='D')
            cartitem_instance = CartItem.objects.filter(cart=cart_instance)
            
            if len(cartitem_instance) == 0:
                raise Exception('No Product in the Cart')
            
            # checking if any product quantity is greater than available stock
            for cartitem in cartitem_instance:
                if cartitem.quantity > cartitem.product.quantity:
                    raise Exception('only '+str(cartitem.product.quantity)+' quantity of product '+str(cartitem.product.name)+' is available')
            
            address_instance = UserAddress.objects.filter(user = request.user, available=True).order_by("id")
            new_address_id = request.GET.get('address_id')
            new_shipping_address_id = request.GET.get('shipping_address_id')


            new_address_filter = address_instance.filter(default_billing = True)
            if len(new_address_filter) == 1:
                new_address = new_address_filter.first()
            else:
                new_address = new_address_filter.none()
            

            new_shipping_address_filter = address_instance.filter(default_shipping=True)
            if len(new_shipping_address_filter) == 1:
                new_shipping_address = new_shipping_address_filter.first()
            else:
                new_shipping_address = new_shipping_address_filter.none()


            return render(request, 'checkout.html',{'cartitem_instance':cartitem_instance, 'addresses':address_instance,'new_address':new_address,'new_shipping_address':new_shipping_address, 'payment_form':payment_form})
        
        except Exception as ex:
            print('cart checkout exception----error')
            print(ex)
            if str(ex) == 'No Product in the Cart' or str(ex) == 'Cart matching query does not exist.':
                messages.add_message(request, messages.WARNING, 'Add some product to the cart')
            else:
                messages.add_message(request, messages.ERROR, str(ex))
            return redirect('CartIndex')
    
    def post(self, request):
        form = PaymentAddressForm(request.POST)

        try:
            cart_instance = Cart.objects.get(user=request.user,status='D')
            try:
                cartitem_instance = CartItem.objects.filter(cart=cart_instance)
                for cartitem in cartitem_instance:
                    if cartitem.quantity > cartitem.product.quantity:
                        raise Exception('only '+str(cartitem.product.quantity)+' quantity of product '+str(cartitem.product.name)+' is available')
            except Exception as ex:
                print(ex,'-------in post of checkout')
                messages.add_message(request, messages.ERROR ,str(ex))
                return redirect('CartIndex')

        except Exception as ex:
            print(ex)
            return redirect('CartIndex')
        if form.is_valid():
            
            billing_address_id = form.cleaned_data.get('billing_address')
            shipping_address_id = form.cleaned_data.get('shipping_address')

            try:
                billing_address = UserAddress.objects.get(id=int(billing_address_id))
                shipping_address = UserAddress.objects.get(id=int(shipping_address_id))
                request.session['billing_address_id'] = billing_address.id
                request.session['shipping_address_id'] = shipping_address.id

            except Exception as ex:
                print(ex)
                messages.add_message(request, messages.ERROR ,"please select valid address")
                return redirect('Checkout')
            return redirect('PaymentPage')
        else:
            print(form.errors,'-----address select form error')
            messages.add_message(request, messages.ERROR ,"please select valid address")

            return redirect('Checkout')


def paymentPage(request):
    if request.method == 'GET':
        authorize_form = PaymentForm()
        try:
            billing_address = UserAddress.objects.get(id=request.session['billing_address_id'])
            shipping_address = UserAddress.objects.get(id=request.session['shipping_address_id'])
            return render(request, 'payment_option.html',{'authorize_form':authorize_form,'shipping_address':shipping_address,'billing_address':billing_address})

        except Exception as ex:
            messages.add_message(request, messages.WARNING, 'Please Select Billing And Shipping Address')
            return redirect('Checkout')

@login_required
def authorizePaymentGateway(request):
    if request.method == 'POST':
        try:
            form = PaymentForm(request.POST)
            billing_address = UserAddress.objects.get(id=request.session['billing_address_id'])
            shipping_address = UserAddress.objects.get(id=request.session['shipping_address_id'])
            if form.is_valid():
                try:
                    cart_instance = Cart.objects.get(user=request.user,status='D')
                    try:
                        cartitem_instance = CartItem.objects.filter(cart=cart_instance)
                        for cartitem in cartitem_instance:
                            if cartitem.quantity > cartitem.product.quantity:
                                raise Exception('only '+str(cartitem.product.quantity)+' quantity of product '+str(cartitem.product.name)+' is available')
                    except Exception as ex:
                        print(ex,'-------in post of checkout')
                        messages.add_message(request, messages.ERROR ,str(ex))
                        return redirect('CartIndex')
                except Exception as ex:
                    print(ex)
                    return redirect('CartIndex')

                # authorize.net settings
                merchantAuth = apicontractsv1.merchantAuthenticationType()
                merchantAuth.name = '6Apw56Hwc'
                merchantAuth.transactionKey = '6N37b2zfsMCJ775B'

                creditCard = apicontractsv1.creditCardType()
                creditCard.cardNumber = str(form.cleaned_data.get('card_number'))
                creditCard.expirationDate = str(form.cleaned_data.get('month'))+'/'+str(form.cleaned_data.get('year'))
                creditCard.cardCode = str(form.cleaned_data.get('cvv'))
                payment = apicontractsv1.paymentType()
                payment.creditCard = creditCard

                duplicateWindowSetting = apicontractsv1.settingType()
                duplicateWindowSetting.settingName = "duplicateWindow"
                duplicateWindowSetting.settingValue = "600"
                settings = apicontractsv1.ArrayOfSetting()
                settings.setting.append(duplicateWindowSetting)

                transactionrequest = apicontractsv1.transactionRequestType()
                transactionrequest.transactionType = "authCaptureTransaction"
                transactionrequest.amount = cart_instance.grand_total()['total']
                transactionrequest.payment = payment
                transactionrequest.transactionSettings = settings


                createtransactionrequest = apicontractsv1.createTransactionRequest()
                createtransactionrequest.merchantAuthentication = merchantAuth
                createtransactionrequest.refId = "MerchantID-0001"
                createtransactionrequest.transactionRequest = transactionrequest
                # Create the controller
                createtransactioncontroller = createTransactionController(
                    createtransactionrequest)
                createtransactioncontroller.execute()

                response = createtransactioncontroller.getresponse()

                if response is not None:
                    # Check to see if the API request was successfully received and acted upon
                    if response.messages.resultCode == "Ok":
                        # Since the API request was successful, look for a transaction response
                        # and parse it to display the results of authorizing the card
                        if hasattr(response.transactionResponse, 'messages') is True:
                
                            if response.transactionResponse.messages.message[0].code == 1:
                                try:
                                    print('transection id----',response.transactionResponse.transId)
                                    cart_instance = Cart.objects.get(user=request.user, status='D')
                                    try:
                                        wishlists = Wishlist.objects.filter(user=request.user, product__in=cart_instance.cartitem_set.all().values('product'))
                                        wishlists.delete()
                                        try:
                                            cartitem_instance = CartItem.objects.filter(cart=cart_instance)
                                            for cartitem in cartitem_instance:
                                                product = Product.objects.get(id=cartitem.product.id)
                                                product.quantity -= cartitem.quantity
                                                product.save()
                                        except Exception as ex:
                                            print(ex, '-----in checkout POST')
                                            pass
                                    except:
                                        print(ex, 'exception in cartview checkout---')
                                    order = Order.objects.create(user= request.user,
                                                                cart = cart_instance,
                                                                total_price = cart_instance.grand_total()['total'],
                                                                address = billing_address,
                                                                shipping_address = shipping_address
                                                                )
                                    order.order_number = 'ORD'+str(order.id)
                                    order.save()
                                    cart_instance.status = 'P'
                                    cart_instance.save()
                                    request.session['order_number'] = order.order_number
                                    request.session['transection_id'] = int(response.transactionResponse.transId)
                                    try:
                                        email_thread = Thread(target=send_mail, args=('Order Details','Transection ID:'+str(int(response.transactionResponse.transId))+'\n'
                                        +'Order Number:'+str(order.order_number)+'\n'+
                                        'Total Amount:'+str(cart_instance.grand_total()['total']),'harshilsuthar.happy@gmail.com',[str(request.user.email)]))
                                        email_thread.start()
                                    
                                    except Exception as ex:
                                        print('email send exception-----:',ex)
                                    
                                    return redirect('PaymentSuccess')
                                
                                
                                except Exception as ex:
                                    print(ex)
                                    try:
                                        request.session['order_id'] = order.id
                                    except Exception as ex:
                                        request.session['order_id'] = None
                                    return redirect('PaymentSuccess')
                            else:
                                try:
                                    return redirect('cartIndex')
                                except Exception as ex:
                                    return redirect('cartIndex')
                        else:
                            return redirect('cartIndex')
            
                    else:
                        print('Transaction fail----warning')
                        print(response.transactionResponse.errors.error[0].errorCode)
                        print(response.transactionResponse.errors.error[0].errorText)
                        return redirect('Checkout')
                else:
                    print('Null Response----warning')
                    return redirect('Checkout')
            else:
                print(form.errors)
                return render(request,'payment_option.html',{'authorize_form':form})
        except Exception as ex:
            print(ex)
            return redirect('PaymentPage')


@login_required
@csrf_exempt
def stripe_payment(request):
    if request.method == 'POST':
        try:
            billing_address = UserAddress.objects.get(id=request.session['billing_address_id'])
            shipping_address = UserAddress.objects.get(id=request.session['shipping_address_id'])
        except Exception as ex:
            print(ex,'-----exception in stripe payment')
            return redirect('Checkout')
        
        try:
            cart_instance = Cart.objects.get(user=request.user,status='D')
            try:
                cartitem_instance = CartItem.objects.filter(cart=cart_instance)
                for cartitem in cartitem_instance:
                    if cartitem.quantity > cartitem.product.quantity:
                        raise Exception('only '+str(cartitem.product.quantity)+' quantity of product '+str(cartitem.product.name)+' is available')
            except Exception as ex:
                print(ex,'-------in post of checkout')
                messages.add_message(request, messages.ERROR ,str(ex))
                return redirect('CartIndex')
        except Exception as ex:
            print(ex)
            return redirect('CartIndex')


        stripe.api_key = 'sk_test_51HZ7mKGfCjKz4qJuErS3nJmQF6wjENE2RkdOrDkAXO8d66R4u1tVze6Ags8IlsX0HhUUc76Z6FL10z3MOcAdAbi400ASif9xdP'
        try:
            YOUR_DOMAIN = 'http://127.0.0.1:8000'
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                            'name':'Happy Checkout',
                            'quantity': 1,
                            'currency': 'inr',
                            'amount': int(eval(cart_instance.grand_total()['total'])*100),
                        }],
                metadata={'cart_id': cart_instance.id, 'billing_address_id':billing_address.id, 'shipping_address_id':shipping_address.id},
                mode='payment',
                success_url=YOUR_DOMAIN+'/stripePaymentOrderHandler?stripe_session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN+'/checkout',
            )
            return JsonResponse({'id': checkout_session.id}, status=200)
        except Exception as ex:
            print(ex,'--------------')
            return JsonResponse({'status':'false'}, status=403)

def stripePaymentOrderHandler(request):
    if request.method == 'GET':
        stripe_session_id = request.GET.get('stripe_session_id')
        stripe.api_key = "sk_test_51HZ7mKGfCjKz4qJuErS3nJmQF6wjENE2RkdOrDkAXO8d66R4u1tVze6Ags8IlsX0HhUUc76Z6FL10z3MOcAdAbi400ASif9xdP"
        stripe_session_object = stripe.checkout.Session.retrieve(stripe_session_id)
        stripe_metadata = stripe_session_object.get('metadata')

        # getting data from stripe metadata
        if stripe_metadata:
            cart_id = stripe_metadata.get('cart_id')
            billing_address_id = stripe_metadata.get('billing_address_id')
            shipping_address_id = stripe_metadata.get('shipping_address_id')
            billing_address = UserAddress.objects.get(id=billing_address_id)
            shipping_address = UserAddress.objects.get(id=shipping_address_id)
            
            # updating product quantity according to order with order management and sendmail
            if cart_id:
                try:
                    print('transection id----',stripe_session_object.get('id'))     
                    cart_instance = Cart.objects.get(user=request.user, status='D')
                    try:
                        wishlists = Wishlist.objects.filter(user=request.user, product__in=cart_instance.cartitem_set.all().values('product'))
                        wishlists.delete()
                        try:
                            cartitem_instance = CartItem.objects.filter(cart=cart_instance)
                            for cartitem in cartitem_instance:
                                product = Product.objects.get(id=cartitem.product.id)
                                product.quantity -= cartitem.quantity
                                product.save()
                        except Exception as ex:
                            print(ex, '-----in checkout POST')
                            pass
                    except Exception as ex:
                        print(ex, 'exception in cartview checkout---')
                    order = Order.objects.create(user= request.user,
                    cart = cart_instance,
                    total_price = cart_instance.grand_total()['total'],
                    address = billing_address,
                    shipping_address = shipping_address
                    )
                    order.order_number = 'ORD'+str(order.id)
                    order.save()
                    cart_instance.status = 'P'
                    cart_instance.save()
                    request.session['order_number'] = order.order_number
                    request.session['transection_id'] = stripe_session_object.get('id')
                    try:
                        email_thread = Thread(target=send_mail, args=('Order Details','Transection ID:'+str(stripe_session_object.get('id'))+'\n'
                        +'Order Number:'+str(order.order_number)+'\n'+
                        'Total Amount:'+str(cart_instance.grand_total()['total']),'harshilsuthar.happy@gmail.com',[str(request.user.email)]))
                        email_thread.start()
                    except Exception as ex:
                        print('email send exception-----:',ex)
                    
                    return redirect('PaymentSuccess')
                except Exception as ex:
                    print(ex)
                    try:
                        request.session['order_id'] = order.id
                    except Exception as ex:
                        request.session['order_id'] = None

                    return redirect('PaymentSuccess')

@login_required
def paymentSuccess(request):
    if request.method == 'GET':
        try:
            transection_id = request.session['transection_id']
            order_number = request.session['order_number']
            order_instance = Order.objects.get(order_number=order_number)
            del request.session['transection_id']
            del request.session['order_number']
            return render(request, 'order_success.html',{'transection_id':transection_id, 'order_number':order_number, 'order':order_instance})


        except Exception as ex:
            print(ex)
            return redirect('index')

def paymentFail(request):
    return render(request, 'order_fail.html')


@login_required
def addAddress(request):

    if request.method == 'GET':
        form = CheckOutForm(user=request.user,available=True)
        return render(request, 'add_address.html', {'form':form})


    if request.method == 'POST':
        form = CheckOutForm(request.POST, user=request.user,available=True)
        if form.is_valid():
            address_instance = form.save(commit=False)
            form.save()

            return HttpResponse('ok')
        else:
            return render(request, 'add_address.html', {'form':form})

@login_required
def edit_address(request,address_id):
    if request.method == 'GET':
        try:
            address = UserAddress.objects.get(id=int(address_id))
            form = AddressForm(instance=address)
            return render(request, 'edit_address.html',{'form':form, 'address':address})
        
        except Exception as ex:
            print(ex)
            return HttpResponse('No Object Found')
    
    if request.method == 'POST':
        try:
            # print('post method called----------')
            address = UserAddress.objects.get(id=int(address_id))
            form = AddressForm(request.POST)
            if form.is_valid():
                form.cleaned_data
                address.__dict__.update(**form.cleaned_data)
                address.country = form.cleaned_data.get('country')
                address.state = form.cleaned_data.get('state')
                address.city = form.cleaned_data.get('city')
                address.user = request.user
                address.available = True
                address.save()
                return HttpResponse('ok')
            else:
                print('there is something wrong with the form', form.errors())
                return render(request, 'edit_address.html',{'form':form, 'address':address})
 
        except Exception as ex:
            return HttpResponse('something went wrong try again after sometime')
            traceback.print_exc()
            print(ex)




# sending mail asynchronisly
class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        msg = EmailMessage(self.subject, self.html_content, EMAIL_HOST_USER, self.recipient_list)
        msg.content_subtype = "html"
        msg.send()
