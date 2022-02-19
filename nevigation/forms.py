from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'type':'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class RegisterForm(UserCreationForm):
    mobile = forms.IntegerField(max_value=9999999999, min_value=999999999, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'email', 'mobile', 'password1', 'password2']

    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # self.fields['username'].widget.attrs = {'class':'form-control'}
        self.fields['first_name'].widget.attrs = {'class':'form-control'}
        self.fields['first_name'].required = True
        self.fields['last_name'].widget.attrs = {'class':'form-control'}
        self.fields['last_name'].required = True
        self.fields['email'].widget.attrs = {'class':'form-control'}
        self.fields['password1'].widget.attrs = {'class':'form-control'}
        self.fields['password2'].widget.attrs = {'class':'form-control'}
        self.fields['password2'].label = 'Confirm Password'
