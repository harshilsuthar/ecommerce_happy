# django imports
from django.shortcuts import render, HttpResponse
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# app imports
from store.models.user_profile import UserProfile
from store.models.order import Order
from store.models.product import Product
from store.models.review import ProductReview
from store.models.address import UserAddress
from store.forms import UserForm, UserProfileForm,ChangePasswordForm


class UserProfileView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        order_page_number = request.GET.get('order_page_number')
        userform = UserForm(instance=request.user)
        productReviewForm = ProductReview()
        try:
            try:
                userProfile = UserProfile.objects.get(user=request.user)
            except ObjectDoesNotExist as ex:
                UserProfile.objects.create(user=request.user, mobile=1234567890)
            except Exception as ex:
                print(ex)
            userprofileform = UserProfileForm(instance=UserProfile.objects.get(user=request.user))
        except Exception as ex:
            print(ex)
            userprofileform = []
        userAddresses = UserAddress.objects.filter(user=request.user,available=True)
        changePasswordForm = ChangePasswordForm()
        non_review_products = Product.objects.all().exclude(Q(parent__productreview__in=ProductReview.objects.filter(user=request.user))|Q(productreview__in=ProductReview.objects.filter(user=request.user)))

        order_instance = Order.objects.filter(
            user=request.user).exclude(cart__cartitem=None).order_by('-id')
        order_paginator = Paginator(order_instance, 6)
        if order_page_number != None:
            try:
                order_instance = order_paginator.get_page(order_page_number)
            except Exception as ex:
                order_instance = order_paginator.get_page(1)
        else:
            order_instance = order_paginator.get_page(1)
        return render(request, 'user_account.html',{
            'userform':userform, 
            'userprofileform':userprofileform, 
            'userAddresses':userAddresses, 
            'order_instance':order_instance, 
            'non_review_products':non_review_products, 
            'changePasswordForm':changePasswordForm,
        })
    
    def post(self, request, *args, **kwargs):
        userform = UserForm(request.POST or None, instance=request.user)
        userprofileform = UserProfileForm(request.POST or None, instance=request.user)
        if userform.is_valid() and userprofileform.is_valid():
            user_instance = userform.save(commit=False)
            userprofile_instance = userprofileform.save(commit = False)
            user_instance.save()
            userprofile_instance.save()
            return HttpResponse('Profile Updated Successfully')
        else:
            return HttpResponse(userform.errors.as_ul()+userprofileform.errors.as_ul())

@login_required
def changePasswordView(request):
    if request.method == 'POST':
        changePasswordForm = ChangePasswordForm(request.POST)
        if changePasswordForm.is_valid():
            
            old_password = changePasswordForm.cleaned_data.get('old_password')
            new_password = changePasswordForm.cleaned_data.get('new_password')
            confirm_password = changePasswordForm.cleaned_data.get('confirm_password')
            validate_old_password = request.user.check_password(old_password)
            if validate_old_password:
                if new_password == confirm_password:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    login(request, user)
                    return HttpResponse('ok')
                else:
                    changePasswordForm.add_error(None, error="new password and repeat password does not match!")
                    return render(request, 'user_account_change_password.html',{'changePasswordForm':changePasswordForm})
            else:
                changePasswordForm.add_error(None, error="please enter correct old password!")
                return render(request, 'user_account_change_password.html',{'changePasswordForm':changePasswordForm})
        else:
            return render(request, 'user_account_change_password.html',{'changePasswordForm':changePasswordForm})

@login_required
def setDefaultAddress(request, address_id):
    if request.method == 'GET':
        if address_id:
            try:
                user_address = UserAddress.objects.get(user=request.user, id=address_id)
                if user_address.address_type == 'S':
                    UserAddress.objects.filter(Q(user=request.user)&Q(Q(address_type=user_address.address_type)|Q(address_type='S&B'))).update(default_shipping=False)
                    user_address.default_shipping = True
                    user_address.save()
                elif user_address.address_type == 'B':
                    UserAddress.objects.filter(Q(user=request.user)&Q(Q(address_type=user_address.address_type)|Q(address_type='S&B'))).update(default_billing=False)
                    user_address.default_billing = True
                    user_address.save()
                else:
                    UserAddress.objects.filter(user=request.user).update(default_billing=False,default_shipping=False)
                    user_address.default_billing = True
                    user_address.default_shipping = True
                    user_address.save()
                return HttpResponse(1)
            except Exception as ex:
                print(ex)
                return HttpResponse(0)

