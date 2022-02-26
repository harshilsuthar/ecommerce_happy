from django.db import models
from django.contrib.auth.models import User

class Country(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return self.name

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state =  models.ForeignKey(State, on_delete=models.CASCADE)
    city =  models.ForeignKey(City, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    default_billing = models.BooleanField(default=False)
    default_shipping = models.BooleanField(default=False)
    address_type = models.CharField(choices=(('S','Shipping'),('B','Billing'),('S&B','Shipping & Billing')), max_length=3)

    def __str__(self):
        return str(self.user.get_full_name()) +' '+ self.address +' '+ self.address_2

