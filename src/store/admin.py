from django.contrib import admin

from .models.product import *
from .models.category import Category, CategoryFilterSelector
from .models.cart import Cart, CartItem, Wishlist
from .models.order import Order
from .models.address import *
from .models.user_profile import UserProfile
from .models.review import ProductReview
from .forms import ProductForm
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django import forms
from django.forms.models import model_to_dict, ModelChoiceField
from django.db.models import Count, Q, F
import itertools
from django.contrib.admin import AdminSite
# Register your models here.

def make_publish(modeladmin, request, queryset):
    queryset.update(is_published=True)

def remove_published_product(modeladmin, request, queryset):
    queryset.update(is_published=False)

def make_available(modeladmin ,request, queryset):
    queryset.update(available=True)

def make_unavailable(modeladmin ,request, queryset):
    queryset.update(available=False)

def increase_quantity_by_1(modeladmin ,request, queryset):
    print(dir(queryset),'+++++++++++dir')
    queryset.update(quantity = F('quantity') + 1)

def increase_quantity_by_10(modeladmin ,request, queryset):
    print(dir(queryset),'+++++++++++dir')
    queryset.update(quantity = F('quantity') + 10)










class AdminProductImage(admin.ModelAdmin):
    list_display = ['product','image']


class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_display = ('name', 'path','available')
    actions = [make_available,make_unavailable]

class CategoryFilter(admin.SimpleListFilter):

    title = 'Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            print(self.value(),'==++++++++')
            products = Product.objects.filter(Q(category__in=Category.objects.get(id=self.value()).get_descendants())|Q(category__id=self.value()))
            return products
        return queryset

class AdminProduct(admin.ModelAdmin):
    list_display = ('name', 'varientProperty', 'productTag', 'is_varient', 'category', 'brand' ,'is_published')
    list_filter = ('is_varient', CategoryFilter, 'brand' ,'is_published','created_on')
    actions=[make_publish,remove_published_product,increase_quantity_by_1,increase_quantity_by_10]
    form = ProductForm

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            '/static/js/product_manage.js',)

    def productTag(self, obj):
        return '\n'.join([m2m.tag_name.name+':'+m2m.value for m2m in obj.product_tag.all()])


    def varientProperty(self, obj):
        return '\n'.join([m2m.productAttribute.name+':'+m2m.value for m2m in obj.varient_property.all()])

    # setting how form looks and which fields are readonly and which fields are excluded
    def get_form(self, request, obj=None,**kwargs):
        # initialize exclude and readonly fields
        self.exclude = []
        self.readonly_fields = []
        # if obj == None:
        #     self.exclude = ['product_tag']
        # if is_varient is selected then make these fields readonly
        if obj and obj.is_varient:
            self.exclude.extend(['product_tag'])
            self.readonly_fields.extend(['varient_property','category','parent','has_varient','is_varient','brand'])
        
        # if has_varient is selected then hide these fields
        if obj and obj.has_varient:
            self.readonly_fields.extend(['parent','has_varient','is_varient'])
        return super(AdminProduct, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):

        #if only changes in form
        if change:
            if form.cleaned_data.get('varient_property') != None:

                # getting old and new changes instance
                old_instance = obj.varient_property.all()
                new_instance = form.cleaned_data['varient_property']

                # updating product varient brand and category if master is updated 
                for product in Product.objects.filter(parent=obj):
                    if form.cleaned_data.get('category'):
                        product.category = form.cleaned_data.get('category')
                    if form.cleaned_data.get('category'):
                        product.brand = form.cleaned_data.get('brand')
                    product.save()



                print(old_instance)
                print(new_instance,'--------new instance')
        
                # getting old category and new one
                if old_instance != new_instance:
                    new_categories = [category['productAttribute__name'] for category in new_instance.values('productAttribute__name').distinct()]
                    old_categories = [category['productAttribute__name'] for category in old_instance.values('productAttribute__name').distinct()]
                    

                    print('old_categories--',old_categories,'\n\n')
                    print('new_categories--',new_categories,'\n\n')

                    old_list_combinations = []
                    new_list_combinations = []


                    # crating product (x) for manytomany relation(ex for color and size make product(X))
                    """
                        for example selecting sizes L, M
                        colors red, yellow then products will be
                        (L,red)
                        (L,yellow)
                        (M,red)
                        (M,yellow)
                    """

                    # product for new changed categories
                    for category in new_categories:
                        new_list_combinations.append(new_instance.filter(productAttribute__name=category))
                    new_list_combinations = list(itertools.product(*new_list_combinations))

                    # product for old categories
                    for category in old_categories:
                        old_list_combinations.append(old_instance.filter(productAttribute__name=category))
                    old_list_combinations = list(itertools.product(*old_list_combinations))

                    print('old_list_combinations----',old_list_combinations,'\n\n')
                    print('new_list_combinations----',new_list_combinations,'\n\n')
                    # print(ol)

                    # new added manytomany relations
                    add_combination = list(set(new_list_combinations)-set(old_list_combinations))
        
                    # old remove manytomany relations
                    remove_combination = list(set(old_list_combinations)-set(new_list_combinations))
                    
                    print('add new combinations----',add_combination,'\n\n')
                    print('delete old combinations----',remove_combination,'\n\n')

                    # making product unavailable for removed manytomany in new update
                    for m2m in remove_combination:
                        try:
                            total_m2m_count = len(m2m)
                            products = Product.objects.annotate(count=Count('varient_property')).filter(count=total_m2m_count,parent=obj)
                            for varient_property in m2m:
                                products = products.filter(varient_property=varient_property)
                            print(products,'====================new filtered products for removing')
                            if len(products) != 0:
                                for product in products:
                                    product.is_published = False
                                    product.save()
                        except Exception as ex:
                            print('exception in admin product delete combination add-----\n',ex)


                    # making product available for added manytomany in new update or creating if product with this relation not available

                    for new_m2m in add_combination:
                        try:
                            if len(new_m2m) != 0:
                                total_m2m_count = len(new_m2m)
                                products = Product.objects.annotate(count=Count('varient_property')).filter(count=total_m2m_count,parent=obj)
                                for m2m in new_m2m:
                                    products = products.filter(varient_property=m2m)
                                print(products,'====================new filtered products')
                                if len(products) != 0:
                                    for product in products:
                                        product.is_published = True
                                        product.save()
                                    print('msg-------------------product is available now')
                                else:
                                    product = Product.objects.create(name=obj.name,brand=obj.brand, price=obj.price, category=obj.category, description=obj.description, product_image= obj.product_image, is_varient=True, has_varient=False, parent=obj)
                                    product.varient_property.add(*new_m2m)
                                    product.save()
                            else:
                                products = Product.objects.filter(parent=obj, varient_property=None)
                                if len(products) != 0:
                                    print('product available at with no m2m')
                                    for product in products:
                                        product.is_published = True
                                        product.save()
                                else:
                                    raise Exception('selected no m2m field creating new product')

                        # creating new product
                        except Exception as ex:
                            print('exception in admin product new combination add-----\n',ex)
                            try:
                                if len(new_m2m) != 0:
                                    product = Product.objects.create(name=obj.name, brand=obj.brand,price=obj.price, category=obj.category, description=obj.description, product_image= obj.product_image, is_varient=True, has_varient=False, parent=obj)
                                    product.varient_property.add(*new_m2m)
                                    product.save()
                                else:
                                    products = Product.objects.filter(parent=obj, varient_property=None)
                                    for product in products:
                                        print(product)
                                        product.is_published = False
                                        product.save()
                                print('new product created --------msg')
                            except Exception as ex:
                                print('error while creating updated product in AdminModel----',ex)
            
            form.save()
            form.save_m2m()
            form.save()


        # if new product gets created
        if not change:
            form.save()
            form.save_m2m()
            instance = form.save()
            print(instance.varient_property.all(),'-=-=-=')
            

            
            # getting distinct categories of new added manytomany
            categories = [category['productAttribute__name'] for category in instance.varient_property.all().values('productAttribute__name').distinct()]
            print(categories,'----------------------\n\n')
            list_combinations = []

            # making PRODUCT of manytomany relation
            for category in categories:
                print(instance.varient_property.filter(productAttribute__name=category),'++++++++++++++')
                list_combinations.append(instance.varient_property.filter(productAttribute__name=category))
            list_combinations = list(itertools.product(*list_combinations))
            print(list_combinations)

            # creating new products for manytomany relation and setting manytomany fields in each product
            if len(list_combinations) == 0 and instance.has_varient == True:
                product = Product.objects.create(name=instance.name, quantity=instance.quantity, price=instance.price, category=instance.category, description=instance.description, product_image= instance.product_image, is_varient=True, has_varient=False, parent=instance, brand=instance.brand)
            else:
                for varient in list_combinations:
                    print(varient,'------------varient')
                    product = Product.objects.create(name=instance.name, quantity=instance.quantity, price=instance.price, category=instance.category, description=instance.description, product_image= instance.product_image, is_varient=True, has_varient=False, parent=instance, brand=instance.brand)
                    product.varient_property.add(*varient)
                    print(product.varient_property,'------------------------')
                    product.save()
                    print(product.varient_property)


class CategoryFilterSelectorAdmin(admin.ModelAdmin):
    list_display = ['category','productAttributeList','tagNameList','available']
    actions = ['make_available','make_unavailable']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            '/static/js/category_filter_selector.js',)

    def productAttributeList(self, obj):
        return '\n'.join([attribute.name for attribute in obj.productAttribute.all()])

    def tagNameList(self, obj):
        return '\n'.join([tag.name for tag in obj.tagName.all()])

class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'available', 'add_to_filter')


class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('productAttribute','value')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id' ,'user','status')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product','quantity')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile')


class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user','first_name', 'last_name', 'address_type', 'default_billing', 'default_shipping','available')


class TagNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'available_to_children', 'available')
    actions = [make_available,make_unavailable]


class TagValueAdmin(admin.ModelAdmin):
    list_display = ('tag_name','value', 'available')
    actions = [make_available,make_unavailable]


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

admin.site.register(Product,AdminProduct)
admin.site.register(ProductAttribute,ProductAttributeAdmin)
admin.site.register(AttributeValue,AttributeValueAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Product_multi_image, AdminProductImage)
admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Category, MyAdmin)
admin.site.register(CategoryFilterSelector, CategoryFilterSelectorAdmin)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(UserAddress,UserAddressAdmin)
admin.site.register(Order)
admin.site.register(ProductReview)
admin.site.register(Banner)
admin.site.register(Brand,BrandAdmin)
admin.site.register(Wishlist)
admin.site.register(TagName, TagNameAdmin)
admin.site.register(TagValue, TagValueAdmin)