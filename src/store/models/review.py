from django.db import models
from store.models.product import Product
from store.models.order import Order
from django.contrib.auth.models import User
from datetime import datetime


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    review_heading = models.CharField(max_length=30)
    review_date = models.DateTimeField(auto_now_add=True)
    review_description = models.CharField(max_length=1000)
    review_rating = models.PositiveIntegerField()
    review_product_image = models.ImageField(upload_to='review_image/', blank=True)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        try:
            return self.product.name+' '+str(self.product.id)+' order:'+str(self.order.id)+' '+str(self.review_rating)
        except:
            return self.product.name+str(self.review_rating)
    

    @staticmethod
    def average_rating(product):
        avg_rating = ProductReview.objects.filter(product=product).aggregate(models.Avg('review_rating'))
        return avg_rating

    @staticmethod
    def user_count(product):
        total_user = ProductReview.objects.filter(product=product).count()
        return total_user
    
    def save(self, *args, **kwargs):
        is_ordered = Order.objects.filter(user=self.user, cart__cartitem__product__parent=self.product)
        if len(is_ordered) != 0:
            print('saving review-------')
            super(ProductReview, self).save(*args, **kwargs)
        else:
            print('could not save review--------------------error while saving in review.py model')
