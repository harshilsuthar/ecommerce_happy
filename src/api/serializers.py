from django.contrib.auth.models import User
from store.models.address import *
from store.models.cart import *
from store.models.category import *
from store.models.order import *
from store.models.product import *
from store.models.review import *
from store.models.user_profile import *
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['mobile','image']


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(many=False)
    class Meta:
        model = User
        fields = ['email','password','first_name','last_name', 'userprofile']
    
    def create(self, validated_data):
        userprofile_data = validated_data.pop('userprofile')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))
        user.username = validated_data.get('email')
        user.save()
        userprofile = UserProfile.objects.create(user=user, **userprofile_data)
        return user


class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),source='product.id')
    class Meta:
        model = Product_multi_image
        fields = '__all__'
    def create(self, validated_data):
        child = Product_multi_image.objects.create(product=validated_data['product']['id'], image=validated_data['Product_multi_image_set']['image'])
        return subject


class ProductSerializer(serializers.ModelSerializer):

    product_multi_image_set = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['status']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product','quantity']
    