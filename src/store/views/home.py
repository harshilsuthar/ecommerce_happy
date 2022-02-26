# django imports
from django.views import View
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Max, Min, Sum, Case, When, Count

# app imports
from store.models.product import *
from store.forms import ReviewForm
from store.models.review import ProductReview
from store.models.cart import Cart, CartItem, Wishlist
from store.models.category import Category, CategoryFilterSelector

# other imports
import json
import datetime
import traceback


def all_available_categories():
    try:
        q = Q()
        all_unavailabel_categories_path_list = [category.path for category in Category.objects.filter(available=False)]
        for unavailable in all_unavailabel_categories_path_list:
            q |= Q(path__startswith=unavailable)
        
        all_available_categories = Category.objects.all().exclude(q | Q(path__in=all_unavailabel_categories_path_list))
        # print(all_unavailabel_categories_path_list, all_available_categories,
        #       '--------category id and available status')
    except Exception as ex:
        print(ex, '------- exception in all available categories')
        all_available_categories = Category.objects.all()
    return all_available_categories


class Index(View):
    def get(self, request, *args, **kwargs):
        try:
            # top latest products
            latest_products = Product.objects.filter(
                is_published=True, parent=None, category__in=all_available_categories()).order_by('-created_on')[:10]
            
            # all banners
            banners = Banner.objects.all()

            # top selling products getting from cartitems which is ordered
            cartitems = CartItem.objects.filter(cart__status='P').values(
                'product__parent').annotate(Sum('quantity')).order_by('-quantity__sum')
            top_product_ids = [data['product__parent'] for data in cartitems]
            preserved = Case(*[When(pk=pk, then=pos)
                               for pos, pk in enumerate(top_product_ids)])
            top_selling_products = Product.objects.filter(
                id__in=top_product_ids, category__in=all_available_categories()).order_by(preserved)[:8]
            

            # if user is authenticated then show wishlist button and its option
            if request.user.is_authenticated:
                wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.filter(user=request.user))
            else:
                wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.none())

            return render(request, 'index.html', {
                'latest_products': latest_products, 
                'top_selling_products': top_selling_products, 
                'banners': banners,
                'wishlist_products':wishlist_products
                })
        except Exception as ex:
            print(ex)
            raise Http404('index not exist')


class Products(View):

    def get(self, request, *args, **kwargs):

        # getting all param from GET method 
        category_id = request.GET.get('category')
        search = request.GET.get('search')
        min_price = request.GET.get('min')
        max_price = request.GET.get('max')
        brandlist = request.GET.get('brand')
        product_tag_list = request.GET.get('product_tag')
        attribute_values_list = request.GET.get('product_attribute')
        page_number = request.GET.get('page')


        # if brand filter is applied then fetching brand ids from url and splitting using _ 
        print(brandlist, type(brandlist),
              '==========++++++++++++ getting from front end')
        try:
            if brandlist and brandlist.strip() != '':
                brandlist = [int(brand_id)
                             for brand_id in brandlist.split('_')]
            else:
                brandlist = []
        except Exception as ex:
            print(ex)
            brandlist = []
        brandlist = [int(brand_id) for brand_id in brandlist]


        # if product tag is applied then get product tag list from url and splitting using _ 
        print(product_tag_list, type(product_tag_list),
              '==========++++++++++++ getting from front end')
        try:
            if product_tag_list and product_tag_list.strip() != '':
                product_tag_list = [int(product_tag)
                                    for product_tag in product_tag_list.split('_')]
            else:
                product_tag_list = []
        except Exception as ex:
            print(ex)
            product_tag_list = []
        

        print(attribute_values_list, type(attribute_values_list),
              '==========++++++++++++ getting from front end')

        # if attribute filter is applied then get attribute values list from url and splitting using _ 
        try:
            if attribute_values_list and attribute_values_list.strip() != '':
                attribute_values_list = [
                    int(attribute_value) for attribute_value in attribute_values_list.split('_')]
            else:
                attribute_values_list = []
        except Exception as ex:
            attribute_values_list = []
            print(ex, '-------attribute value list exception')


        # get all published products
        products = Product.objects.filter(
            is_published=True, category__in=all_available_categories())


        # if category is applied
        if category_id:

            # getting category filter for filter selection
            try:
                category_filter = CategoryFilterSelector.objects.get(category__id=category_id, available=True)
            except Exception as ex:
                print(ex,'---------in category_filter_selector in home')
                category_filter = CategoryFilterSelector.objects.none()


            # get all products related to this category or decendants of this category
            products = products.filter(Q(category__in=Category.objects.get(
                id=int(category_id), available=True).get_descendants().filter(available=True)) | Q(category__id=int(category_id)))
            print(products,'-----------------products')
            
            if not category_filter:

                # get all product tags whose category is current category to send list to frontend for showing filters
                product_tags = TagName.objects.filter(tagvalue__product__in=products).distinct()

                # get all product attributes whose category is current category to send list to frontend for showing filters
                product_attributes = ProductAttribute.objects.filter(attributevalue__product__in=products).distinct()
                
                print(product_attributes,'-----------product attribute')

            else:
                product_tags = category_filter.tagName.filter(tagvalue__product__in=products).distinct()
                
                product_attributes = category_filter.productAttribute.filter(attributevalue__product__in=products).distinct()
                
                print(product_attributes,'-----------product attribute')
            
            

            
            
        # if category is not applied then return product tags and product attributes null list
        else:
            product_attributes = ProductAttribute.objects.none()
            product_tags = TagName.objects.none()
    

        # if search is applied then filter products against search value
        if search:
            products = products.filter(
                Q(name__contains=search) | Q(description__contains=search))

        # get tag_names list from tag_values
        tag_name_list = TagName.objects.filter(
            tagvalue__in=product_tag_list).distinct()
        print(tag_name_list, '---------------tag name list')


        # get product attribute list from attribute values list
        product_attribute_list = ProductAttribute.objects.filter(
            attributevalue__in=attribute_values_list)


        # if attribute filter is applied then filter products
        if len(attribute_values_list) != 0:
            products = products.filter(
                varient_property__id__in=attribute_values_list)

        # if product tag filter is applied then filter products
        if len(product_tag_list) != 0:
            for tagname in tag_name_list:
                print(tagname.tagvalue_set.all())
                products = products.filter(
                    product_tag__in=tagname.tagvalue_set.filter(id__in=product_tag_list))

        category_brand = products

        # getting all parent products from filtered products
        products = products.filter(parent=None).distinct()

        # if brand filter is applied then filter products
        if len(brandlist) != 0:
            try:
                products = products.filter(brand__id__in=brandlist)
            except Exception as ex:
                pass

        try:
            # gettting max and min price from filtered products to send it to frontend
            max_product_price = category_brand.aggregate(Max('price'))[
                'price__max']
            min_product_price = category_brand.aggregate(Min('price'))[
                'price__min']

            # if max and min price filter is applied then set current filterd price and max min price for price silder
            if max_price and min_price:
                try:
                    set_max_price = max_price
                    set_min_price = min_price
                    products = products.filter(price__gte=min_price)
                    products = products.filter(price__lte=max_price)
                except Exception as ex:
                    set_max_price = max_product_price
                    set_min_price = min_product_price
            else:
                set_max_price = max_product_price
                set_min_price = min_product_price

        except Exception as ex:
            print(ex, 'error in home-product max and min price not working ')
            max_product_price = 5000
            min_product_price = 0
            set_max_price = max_product_price
            set_min_price = min_product_price

        # send current selected category and filtered brand according to category
        if category_id:
            current_category = Category.objects.get(id=int(category_id))
            brands = Brand.objects.filter(Q(Q(product__category__in=Category.objects.get(id=int(category_id)).get_descendants()) | Q(product__category__id=int(
                category_id))) & Q(product__is_published=True, product__parent=None)).distinct().annotate(product_count=Count('product')).order_by('-product_count')
        else:
            current_category = Category.objects.none()
            brands = Brand.objects.filter(product__is_published=True, product__parent=None).distinct(
            ).annotate(product_count=Count('product')).order_by('-product_count')

        # creating product pagination
        products = products.order_by('-id')
        paginator = Paginator(products, 12)

        # send requested paginated products
        if page_number != None:
            try:
                products = paginator.get_page(page_number)
            except Exception as ex:
                products = paginator.get_page(1)
        else:
            products = paginator.get_page(1)

        # sending all categories list
        categories = Category.get_annotated_list()
        if request.user.is_authenticated:
            wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.filter(user=request.user))
        else:
            wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.none())

        data = {'products': products,
                'categories': categories,
                'max': max_product_price,
                'min': min_product_price,
                'set_max_price': set_max_price,
                'set_min_price': set_min_price,
                'brands': brands,
                'product_tags': product_tags,
                'product_attribute_list': product_attributes,
                'current_category': current_category,
                'wishlist_products':wishlist_products}
        return render(request, 'products.html', data)


def getCurrentProductQuantity(request):
    if request.method == 'GET':
        try:
            product_id = request.GET.get('product_id')
            latest_product_quantity = Product.objects.get(
                id=int(product_id)).quantity
            return HttpResponse(latest_product_quantity)
        except Exception as ex:
            print(ex)
            return HttpResponse(0)


def product_detail_view(request, id):
    if request.method == 'GET':
        # simpily return product details with rating and user count
        try:
            product = get_object_or_404(Product, id=id, category__in=all_available_categories())
            
            if(product.parent == None):
                return redirect('product_detail_view', product.get_first_child().id)
            review_form = ReviewForm(
                initial={'user': request.user, 'product': product.parent})
            
            if request.user.is_authenticated:
                non_review_products = Product.objects.filter(cartitem__cart__order__cart__cartitem__product=product).exclude(
                    Q(parent__productreview__in=ProductReview.objects.filter(user=request.user)) | Q(productreview__in=ProductReview.objects.filter(user=request.user)))
            else:
                non_review_products = Product.objects.none()
            product_review = ProductReview.objects.filter(
                product=product.parent)
            # (product_review,'*********')
            product_varient = Product.objects.filter(
                parent=product.parent, is_published=True)
            if request.user.is_authenticated:
                wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.filter(user=request.user))
            else:
                wishlist_products = Product.objects.filter(wishlist__in=Wishlist.objects.none())
            return render(request, 'product_details.html', {
                'product': product, 
                'product_review': product_review, 
                'product_varient': product_varient, 
                'review_form': review_form, 
                'non_review_products': non_review_products,
                'wishlist_products':wishlist_products
                })

        except Exception as ex:
            traceback.print_exc()
            print(ex)
            return redirect('products')


def page_not_found(request, exception):
    return render(request, '404.html')


def internal_server_error(request):
    return render(request, '500.html')


@login_required
def update_product_tag_admin(request):
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        # print('calling module ==========',category_id)
        try:
            if category_id:
                tag_name = TagName.objects.filter(Q(category__in=Category.objects.get(
                    id=int(category_id)).get_ancestors()) | Q(category__id=int(category_id)))
                tag_value = TagValue.objects.filter(tag_name__in=tag_name)
                # print(tag_value)
            else:
                tag_value = TagValue.objects.none()
                # print(tag_value)
        except Exception as ex:
            print(ex)
            tag_value = TagValue.objects.none()
        finally:
            return render(request, 'admin_tag_value_m2m.html', {'option_list': tag_value})


@login_required
def update_product_attribute_admin(request):
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        try:
            if category_id:
                product_attribute = ProductAttribute.objects.filter(Q(category__in=Category.objects.get(
                    id=int(category_id)).get_ancestors()) | Q(category__id=int(category_id))|Q(category=None))
                attribute_value = AttributeValue.objects.filter(
                    productAttribute__in=product_attribute)
                # print(attribute_value,'++++++++')
            else:
                attribute_value = AttributeValue.objects.none()
        except Exception as ex:
            print(ex)
            attribute_value = AttributeValue.objects.none()
        return render(request, 'admin_attribute_m2m.html', {'option_list': attribute_value})


def update_product_attribute_name_list(request):
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        try:
            if category_id:
                product_attribute = ProductAttribute.objects.filter(Q(category__in=Category.objects.get(
                    id=int(category_id)).get_ancestors()) | Q(category__id=int(category_id)))
            else:
                product_attribute = ProductAttribute.objects.none()
        except Exception as ex:
            print(ex,'in update_product_attribute_name_list exception')
            product_attribute = ProductAttribute.objects.none()
        finally:
            html_response = ''
            for attribute in product_attribute:
                html_response += '<option value="attribute_id">attribute_name</option>'.replace('attribute_id',str(attribute.id)).replace('attribute_name',str(attribute.name))
            return HttpResponse(html_response)


def update_product_tag_name_list(request):
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        # print('calling module ==========',category_id)
        try:
            if category_id:
                tag_name = TagName.objects.filter(Q(category__in=Category.objects.get(
                    id=int(category_id)).get_ancestors()) | Q(category__id=int(category_id)))
            else:
                tag_name = TagName.objects.none()
        except Exception as ex:
            print(ex, '====in update_product_tag_name_list exception')
            tag_name = TagName.objects.none()
        finally:
            html_response = ''
            for tag in tag_name:
                html_response += '<option value="tag_id">tag_name</option>'.replace('tag_id',str(tag.id)).replace('tag_name',str(tag.name))
            return HttpResponse(html_response)
