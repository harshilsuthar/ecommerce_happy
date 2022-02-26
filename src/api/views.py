from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from store.models.address import *
from store.models.cart import *
# from store.models.category import *
from store.models.order import *
from store.models.product import *
from store.models.review import *
from store.models.user_profile import *
from .serializers import *
# Create your views here.

class UserRegisterViewset(APIView):

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST,exception=True)


class UserAuthTokenViewSet(APIView):
    def post(self, request, format=None):
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(username=email, password=password)
            print(user)
            if user:
                token = Token.objects.get_or_create(user=user)
                print(token[0].key)
                return Response(data={'token':token[0].key},status=status.HTTP_201_CREATED)
            else:
                print('user not authenticated')
                return Response(data={'exception':'email or password are invalid'},status=status.HTTP_401_UNAUTHORIZED, exception=True)
        except Exception as ex:
            print(ex)
            return Response(data={'exception':str(ex)},status=status.HTTP_401_UNAUTHORIZED)


class CustomAPIView(APIView):
    def get_permissions(self):
        # Instances and returns the dict of permissions that the view requires.
        return {key: [permission() for permission in permissions] for key, permissions in self.permission_classes.items()}

    def check_permissions(self, request):
        # Gets the request method and the permissions dict, and checks the permissions defined in the key matching
        # the method.
        method = request.method.lower()
        for permission in self.get_permissions()[method]:
            if not permission.has_permission(request, self):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )


class ProductViewSet(CustomAPIView):
    permission_classes = {'get':[permissions.IsAuthenticated], 'post':[permissions.IsAdminUser]}
    
    def get(self, request, format=None):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailsViewSet(CustomAPIView):
    permission_classes = {'get':[permissions.IsAuthenticated], 'post':[permissions.IsAdminUser]}

    def get(self, request, format=None, *args, **kwargs):
        product = Product.objects.filter(id=kwargs['pk'])
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request,format=None, *args, **kwargs):
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartViewSet(ModelViewSet):
    authentication_classes =[SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes =[IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    def create(self, request, format=None):
        print()
        serializer = CartSerializer(data=request.data)
        
        if serializer.is_valid():
            print('serializer is valid')
            if len(Cart.objects.filter(user=request.user, status='D'))>0:
                return APIView.permission_denied(self, request, message='cart is already exist', code=status.HTTP_400_BAD_REQUEST)
            
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.data.get('user') != None:
            return ModelViewSet.permission_denied(self, request, message="can't change owner of the cart", code=status.HTTP_403_FORBIDDEN)
        else:
            return super(CartViewSet,self).update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            cart_instance = Cart.objects.get(id=int(kwargs.get('pk')))
        except Exception as ex:
            print(ex)
            return ModelViewSet.permission_denied(self, request, message="cart not exist", code=status.HTTP_403_FORBIDDEN)
        
        print(cart_instance.user.id, request.user.id)
        if cart_instance.user == request.user:
            return super(CartViewSet, self).retrieve(request, *args, **kwargs)
        else:   
            return ModelViewSet.permission_denied(self, request, message="can't check other user's cart", code=status.HTTP_403_FORBIDDEN)
        
 
class CartPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        cart = request.META.get('cart')
        if not cart:
            return True
        user = Cart.objects.filter(id = int(cart)).user.id
        if request.user.id == user:
            return True
        else:
            return False

    permission_classes = [permissions.IsAuthenticated]


class CartItemViewSet(ModelViewSet):
    authentication_classes =[SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes =[IsAuthenticated, CartPermission]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def list(self, request):
        self.queryset = CartItem.objects.filter(cart__user = request.user, cart__status='D')
        return super(CartItemViewSet, self).list(request)
    
    def create(self, request):
        
        cart_instance,stat = Cart.objects.get_or_create(user=request.user, status='D')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cartitem_instance,stat = CartItem.objects.get_or_create(cart=cart_instance, product=Product.objects.get(id = int(serializer.data.get('product'))), price_ht=Product.objects.get(id = int(serializer.data.get('product'))).price)
        if stat == False:
            cartitem_instance.quantity += serializer.data.get('quantity')
        else:
            cartitem_instance.quantity=serializer.data.get('quantity')
        cartitem_instance.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        try:
            print(request.user.id)
            print(kwargs.get('pk'))
            cart_instance = Cart.objects.get(user=request.user, status='D',cartitem__id=kwargs.get('pk'))
            cartitem_instance = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            CartItem.objects.filter(id=kwargs.get('pk')).update(**serializer.data)
            print(CartItem.objects.get(id=kwargs.get('pk')).quantity)
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        except Exception as ex:
            print(ex)
            return Response(data=request.data, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        try:
            cart_instance = Cart.objects.get(user=request.user, status='D', cartitem__id=kwargs.get('pk'))
            return super(CartItemViewSet, self).destroy(request, *args, **kwargs)
        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_403_FORBIDDEN)