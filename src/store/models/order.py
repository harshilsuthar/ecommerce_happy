from django.db import models
from store.models.cart import Cart
from store.models.address import UserAddress
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(unique=True, max_length=20, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.RESTRICT)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    total_price = models.DecimalField(decimal_places=2,max_digits=10)
    address = models.ForeignKey(UserAddress, on_delete=models.DO_NOTHING)
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.DO_NOTHING, related_name='shipping_address')
    def __str__(self):
        return 'order'+str(self.id)+' '+str(self.cart)
