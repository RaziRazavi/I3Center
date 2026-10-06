from django import forms
from accounts.models import User


class CartForm(forms.Form): # creates integer input for getting quantity from user
    quantity  = forms.IntegerField(label='تعداد', min_value= 1, widget=forms.NumberInput(attrs={'class': 'form-control'}))


class OrderForm(forms.ModelForm): #creates inputs base on some fields from a table in database & inherits their features
    class Meta:
        model = User # gets from this table
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'state', 'city', 'address', 'zip_code') # these fields
        widgets = {
            'phone_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }  # adds bootstrap class and declare their input types


class CouponForm(forms.Form): # creates text input for getting coupon code from user
    code = forms.CharField(label='کد تخفیف', required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                    'placeholder': 'کد تخفیف رو اینجا وارد کنید'}))