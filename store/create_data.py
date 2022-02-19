from store.models.product import Product, Category, AttributeValue, TagValue, Brand
from django.core.files import File
for i in range(1000):
    product = Product.objects.create(name='test_product'+str(i),
                                    category=Category.objects.get(id=3),
                                    price=100,
                                    quantity=10,
                                    description='test product description',
                                    has_varient=True,
                                    is_varient=False,
                                    is_published=True,
                                    brand=Brand.objects.get(id=6),
                                    )
    product.product_image.save('temp_image'+str(i)+'.jpg',File(open('D:/Happy/django-projects/ecommerce/store/temp_image.jpg','rb')))
    varient_product_1 = Product.objects.create(name=product.name,
                                    category=product.category,
                                    price = product.price,
                                    quantity = product.quantity,
                                    description=product.description,
                                    is_varient=True,
                                    has_varient=False,
                                    is_published=True,
                                    brand=product.brand,
                                    parent=product)
    varient_product_1.product_image.save('temp_image_varient_1'+str(i)+'.jpg',File(open('D:/Happy/django-projects/ecommerce/store/temp_image.jpg','rb')))
    varient_product_2 = Product.objects.create(name=product.name,
                                    category=product.category,
                                    price = product.price,
                                    quantity = product.quantity,
                                    description=product.description,
                                    is_varient=True,
                                    has_varient=False,
                                    is_published=True,
                                    brand=product.brand,
                                    parent=product)
    varient_product_2.product_image.save('temp_image_varient_2'+str(i)+'.jpg',File(open('D:/Happy/django-projects/ecommerce/store/temp_image.jpg','rb')))
    varient_product_3 = Product.objects.create(name=product.name,
                                    category=product.category,
                                    price = product.price,
                                    quantity = product.quantity,
                                    description=product.description,
                                    is_varient=True,
                                    has_varient=False,
                                    is_published=True,
                                    brand=product.brand,
                                    parent=product)
    varient_product_3.product_image.save('temp_image_varient_3'+str(i)+'.jpg',File(open('D:/Happy/django-projects/ecommerce/store/temp_image.jpg','rb')))
    attribute_1 = AttributeValue.objects.get(id=35)
    attribute_2 = AttributeValue.objects.get(id=36)
    attribute_3 = AttributeValue.objects.get(id=38)
    attribute_4 = AttributeValue.objects.get(id=43)
    product.varient_property.add(attribute_1,attribute_2,attribute_3,attribute_4)
    varient_product_1.varient_property.add(attribute_1,attribute_4)
    varient_product_2.varient_property.add(attribute_2,attribute_4)
    varient_product_3.varient_property.add(attribute_3,attribute_4)
    product.save()
    varient_product_1.save()
    varient_product_2.save()
    varient_product_3.save()




from store.models.cart import Cart, CartItem
from store.models.product import Product, Category, AttributeValue, TagValue, Brand
from django.contrib.auth.models import User
from django.core.files import File

cart,status = Cart.objects.get_or_create(user= User.objects.get(id=1), status='D')

for product in Product.objects.filter(category__id=3, is_published=True,is_varient=True)[:100]:
    cartitem,status = CartItem.objects.get_or_create(product=product, quantity=1,price_ht=product.price, cart=cart)