from django.db import models
from .product import Product
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Sum, F, FloatField, DecimalField
import decimal

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
    updated_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=(('D','draft'),('O','ordered'),('P','paid')))
    def __str__(self):
        return str(self.user)+' cart'+str(self.id)
    
    def grand_total(self):
        cart_count_value = CartItem.objects.filter(cart=self).aggregate(total = Sum(F('quantity')*F('price_ht'), output_field = FloatField()))
        cart_count_value = {'total':"{:.2f}".format(cart_count_value['total'])}
        return cart_count_value
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_ht = models.DecimalField(decimal_places=2, blank=True, null=True,max_digits=10)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)

    def sub_total(self):
        return self.price_ht * self.quantity
    
    def __str__(self):
        return 'cart '+str(self.cart.id)+' cartitem '+str(self.id) + str(self.product)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product)
    