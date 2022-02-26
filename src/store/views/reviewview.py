# django imports
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# app imports 
from store.models.product import Product
from store.models.order import Order
from store.forms import ReviewForm


class ReviewView(LoginRequiredMixin, View):
    def get(self, request):
        product_id = request.GET.get('product_id')
        order_id = request.GET.get('order_id')
        try:
            if(product_id and order_id):
                product = Product.objects.get(id=int(product_id)).parent
                order = Order.objects.get(id=int(order_id))
                review_form = ReviewForm(initial={'product':product, 'order':order, 'user':request.user})
                return render(request, 'review_form.html', {'review_form':review_form})
        except Exception as ex:
            print(ex)
            return render(request, 'review_form.html')

    def post(self, request):
        form = ReviewForm(request.POST)
        if form.is_valid():
            instance = form.save()

            return redirect('product_detail_view', id=form.cleaned_data['product'].get_first_child().id)
        else:
            print(form.errors.as_data(), ' not valid')
            return redirect('product_detail_view', id=form.cleaned_data['product'].get_first_child().id)


@login_required
def rating(request):
    if request.method == 'GET':
        try:
            product_id = int(request.GET.get('product_id'))
            product = Product.objects.get(id=int(product_id))
            rating = product.get_ratings()
            rating_user_count = product.get_review_user_count()
            response = {'rating':rating, 'rating_user_count':rating_user_count}
        except Exception as ex:
            response=dict()
            print(ex,'----exception in reviewview > rating no product found')
        return JsonResponse(response)