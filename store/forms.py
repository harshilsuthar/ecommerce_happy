from django.contrib.auth.models import User
from store.models.user_profile import UserProfile
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.forms import ModelForm
from store.models.product import Product, TagValue
from store.models.address import *
from datetime import datetime
from store.models.review import ProductReview


class CheckOutForm(forms.ModelForm):
    
    class Meta:
        model = UserAddress
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        self._available = kwargs.pop('available')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {'class': 'form-control'}
        self.fields['last_name'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].widget.attrs = {'class': 'form-control'}
        self.fields['address'].widget.attrs = {'class': 'form-control'}
        self.fields['address_2'].widget.attrs = {'class': 'form-control'}
        self.fields['country'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['country'].empty_label = 'Select Country'
        self.fields['state'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['state'].empty_label = 'Select State'
        self.fields['city'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['city'].empty_label = 'Select City'
        self.fields['address_type'].widget.attrs = {'class':'custom-select d-block w-100'}
    def save(self, commit=True):
        inst = super(CheckOutForm, self).save(commit=False)
        inst.user = self._user
        inst.available = self._available
        if commit:
            inst.save()
            self.save_m2m
        return inst


class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {'class': 'form-control'}
        self.fields['last_name'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].widget.attrs = {'class': 'form-control'}
        self.fields['address'].widget.attrs = {'class': 'form-control'}
        self.fields['address_2'].widget.attrs = {'class': 'form-control'}
        self.fields['country'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['country'].empty_label = 'Select Country'
        self.fields['state'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['state'].empty_label = 'Select State'
        self.fields['city'].widget.attrs = {
            'class': 'custom-select d-block w-100'}
        self.fields['city'].empty_label = 'Select City'
        self.fields['address_type'].widget.attrs = {'class':'custom-select d-block w-100'}


class PaymentForm(forms.Form):
    months = [i for i in zip(range(1, 13), range(1, 13))]
    years = [i for i in zip(
        range(datetime.now().year, datetime.now().year+10), range(datetime.now().year, datetime.now().year+10))]
    name_on_card = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    card_number = forms.CharField(max_length=16, min_length=16, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'type': 'tel'}))
    month = forms.ChoiceField(choices=months, widget=forms.Select(
        attrs={'class': 'form-control'}), label='Expiration Month', initial=datetime.now().month)
    year = forms.ChoiceField(choices=years, widget=forms.Select(
        attrs={'class': 'form-control'}), label='Expiration Year')
    cvv = forms.CharField(max_length=3, min_length=3, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'type': 'tel'}), label='CVV')

class PaymentAddressForm(forms.Form):
    billing_address = forms.CharField(widget=forms.HiddenInput())
    shipping_address = forms.CharField(widget=forms.HiddenInput())

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['review_description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': '4'})
        self.fields['review_description'].label = 'Description'
        self.fields['review_rating'].widget = forms.TextInput(attrs={'type': 'hidden', 'max': 5, 'min': 1, 'required': ''})
        self.fields['review_rating'].label = 'Rating'
        self.fields['user'].widget = forms.TextInput(attrs={'type': 'hidden'})
        self.fields['product'].widget = forms.TextInput(attrs={'type': 'hidden'})
        self.fields['order'].widget = forms.TextInput(attrs={'type': 'hidden'})
        # self.fields['review_date'].widget = forms.TextInput(attrs={'type': 'hidden'})
        self.fields['review_heading'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['review_heading'].label = 'Title'


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {'class': 'form-control'}
        self.fields['last_name'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].widget.attrs = {'class': 'form-control'}
        self.fields['email'].required = True


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ("mobile",)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['mobile'].widget.attrs = {'class': 'form-control', 'type':'tel'}


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'required': ''}), required=True)
    new_password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'required': ''}), required=True)
    confirm_password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'required': ''}), required=True)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'category', 'description', 'product_image',
                  'brand', 'is_varient', 'has_varient', 'varient_property', 'product_tag', 'parent']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
