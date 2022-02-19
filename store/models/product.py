from django.db import models
from .category import Category
from store.tasks import imageResize
import store
import datetime
from django.core.exceptions import ValidationError

class Product(models.Model):

    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2,default=0,max_digits=10)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=300, default='', null=True, blank=True)
    product_image = models.ImageField(upload_to='')
    product_tag = models.ManyToManyField('store.TagValue', blank=True)
    is_varient = models.BooleanField(default=False)
    has_varient = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    varient_property = models.ManyToManyField(to='store.AttributeValue', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey('store.Brand', on_delete=models.RESTRICT)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        # long name for varients
        if self.parent:
            return self.name+' '+self.category.name+' (category'+str(self.category.id)+') '+str(self.id)+' '+str([value['value'] for value in self.varient_property.all().values()])+str(' published' if self.is_published else '')
        # name for master product
        else:
            return self.name+' '+self.category.name+' (category'+str(self.category.id)+') '+str(self.id)+' master'+str(' published' if self.is_published else '')

    
    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.old_image = self.product_image

    def check_any_child_available(self):
        print('calling-----------------------------------')
        if self.parent:
            return False
        else:
            return any([product.is_published for product in self.product_set.all()])

    @staticmethod
    def get_all_products():
        return Product.objects.all().order_by('?')

    @staticmethod
    def get_all_products_by_categoryId(categoryId):
        if categoryId:
            return Product.objects.filter(category=categoryId).order_by('?')
        else:
            return Product.get_all_products()

    
    def get_ratings(self):
        return store.models.review.ProductReview.average_rating(self.parent)['review_rating__avg']

    def get_first_child(self):
        product = Product.objects.filter(parent=self).first()
        return product

    def get_review_user_count(self):
        return store.models.review.ProductReview.user_count(self.parent)
    
    def save(self, *args, **kwargs):
    
        
        super(Product, self).save(*args, **kwargs)
        # product = Product.objects.get(id=self.id)
        
        # product.refresh_from_db()
        # print(product.varient_property.all())
        # if self.id == None:
        #     super(Product, self).save(*args, **kwargs)
        #     print('new object created')
        #     if self.has_varient == True:
        #         print('has varient true')
        #         for varient in self.varient_property.all():
        #             print(varient,'------------varient')
        #             product = Product.objects.create(name=self.name, price=self.price, category=self.category, description=self.description, product_image= self.image, is_varient=True, has_varient=False, parent=self)
        #             product.varient_property.add(varient)
        #             product.save()
        # else:
        #     super(Product, self).save(*args, **kwargs)
            
    
        if self.old_image != self.product_image:
            new_image = imageResize(self.product_image.path)


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    

class Product_multi_image(models.Model):
    image = models.ImageField(upload_to='')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    def __init__(self, *args, **kwargs):
        super(Product_multi_image, self).__init__(*args, **kwargs)
        self.old_image = self.image

    def save(self, *args, **kwargs):
        super(Product_multi_image, self).save(*args, **kwargs)
        if self.old_image != self.image:
            new_image = imageResize(self.image.path)


class Banner(models.Model):

    name = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banners')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    # attribute = models.ForeignKey(AttributeList, on_delete=models.RESTRICT, default=1)
    name = models.CharField(max_length=30)
    add_to_filter = models.BooleanField()
    available = models.BooleanField()
    class Meta:
        unique_together = (('name',),)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    productAttribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=30)
    available = models.BooleanField(default=True)

    def __str__(self):
        return str(self.productAttribute.__str__()) +' '+ self.value


class TagName(models.Model):
    name = models.CharField(max_length=30)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    available_to_children = models.BooleanField(default=False)
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def is_tag_value_available(self):
        if TagValue.objects.filter(tag_name = self, available=True).count():
            return True
        else:
            return False               


class TagValue(models.Model):
    tag_name = models.ForeignKey(TagName, on_delete=models.CASCADE)
    value = models.CharField(max_length=30)
    available = models.BooleanField(default=False)
    def __str__(self):
        return str(self.tag_name) +':'+ str(self.value)
    