from django import template
from store.models.product import Product, TagName, TagValue, Category, AttributeValue, ProductAttribute
from store.models.review import ProductReview
from django.db.models import Q
register = template.Library()
from math import ceil


@register.filter(name='brand_counter')
def brand_counter(brand):
    try:
        ct = 0
        for product in brand.product_set.all():
            # print(product)
            if product.parent == None:
                ct += 1
        brand_count = ct
        # print(category_count)
        return brand_count
    except Exception as ex:
        print(ex, 'exception in category_counter templatetag')
        return 0

@register.filter(name='tag_filter')
def tag_filter(current_category):
    try:
        category_id = current_category.id
        # print(category_id,'------------category id')
        products = Product.objects.filter(Q(category__in=Category.objects.get(id=int(category_id)).get_descendants())|Q(category__id=int(category_id)))
        # print(products,'--------products in tag_filter')
        tag_value_filter = TagValue.objects.filter(product__in=products).distinct()
        # print(tag_value_filter,'---------')
        return tag_value_filter
    except Exception as ex:
        print(ex)
        return TagValue.objects.none()


@register.filter(name='attribute_filter')
def attribute_filter(current_category):
    try:
        category_id = current_category.id
        # print(category_id,'------------category id')
        products = Product.objects.filter(Q(category__in=Category.objects.get(id=int(category_id)).get_descendants())|Q(category__id=int(category_id)))
        # print(products,'--------products in attribute_filter')
        attribute_value_filter = AttributeValue.objects.filter(product__in=products).distinct()
        # print(attribute_value_filter,'---------')
        return attribute_value_filter
    except Exception as ex:
        print(ex)
        return TagValue.objects.none()

@register.filter(name='dict_value_get')
def dict_value_get(dictionary, key):
    return dictionary.get(str(key))


@register.filter(name='cookie_grand_total')
def cookie_grand_total(cookie_dict):
    grand_total = 0
    for product_id, quantity in cookie_dict.items():
        print(int(product_id),int(quantity), '-------cookie grand total product id and quantity') 
        product = Product.objects.get(id=int(product_id))
        grand_total += product.price * int(quantity)

    return grand_total
    pass

@register.filter(name='is_category_available')
def is_category_available(category):

    category_and_ancestors = [single_category.available for single_category in category.get_ancestors()]
    category_and_ancestors.append(category.available)
    if category.available == False or True if False in category_and_ancestors else False:
        # print('false')
        return False
    else:
        # print('true')
        return True

@register.filter(name='shipping_address_count')
def shipping_address_count(addresses):
    shipping_count = addresses.filter(Q(address_type = 'S')|Q(address_type='S&B')).count()
    return shipping_count

@register.filter(name='billing_address_count')
def billing_address_count(addresses):
    billing_count = addresses.filter(Q(address_type = 'B')|Q(address_type='S&B')).count()
    return billing_count


@register.filter(name='non_review_product')
def non_review_product(order,product):
    try:
        if ProductReview.objects.get(order=order, product=product):
            return False
        else:
            return True
    except Exception as ex:
        # print(ex)
        return True


@register.filter(name='pagination_html')
def pagination_html(order):
    order_items_count = order.cart.cartitem_set.count()
    output_html_sample = '<li class="page-item"><a class="page-link" page-number=page_number_1>page_number_count</a></li>'
    output_html = ""
    print(order_items_count,'--------order item count')
    for i in range(1, ceil(order_items_count/2)+1):
        if i != 1:
            if i>3:
                output_html += output_html_sample.replace('page_number_1',str(i)).replace('page_number_count',str(i)).replace('class="page-item"','class="page-item d-none"')
            else:
                output_html += output_html_sample.replace('page_number_1',str(i)).replace('page_number_count',str(i))
        else:
            output_html += output_html_sample.replace('page_number_1',str(i)).replace('page_number_count',str(i)).replace('class="page-item"','class="page-item active"')

    return output_html