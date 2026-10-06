from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from accounts.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تایید رمز عبور', widget=forms.PasswordInput)

    class Meta:  # we inherit user model for using its ready fields and save mechanism to save password and other fields
        model = User # from this table
        fields = ('phone_number', 'email', 'first_name', 'last_name', 'state', 'city', 'address', 'zip_code') # these fields

    def clean(self):  # overrides built-in clean function to check entry password inputs
        cd = super().clean()
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords must match')

    def save(self, commit=True):  # overrides save build-in function to save password in user model table
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text="برای تغییر رمز عبور <a href='../password'>اینحا کلیک کنید</a>")
            # we use Django built-in change password mechanism due to the fact the password field is untouchable
    class Meta:
        model = User # from this table
        fields = ('phone_number', 'email', 'password', 'first_name', 'last_name', 'city', 'state', 'address',
                  'zip_code', 'is_active', 'is_staff', 'is_superuser', 'last_login') # these fields


class UserRegisterForm(forms.Form): # creates form and adds bootstrap classes for getting data from user
    phone_number = forms.CharField(label='شماره تماس', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='ایمیل', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='اسم', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='فامیل', widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(label='شهر', widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label='استان', widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label='آدرس', widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(label='کد پستی', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                                'placeholder': 'Type your password'}))
    password2 = forms.CharField(label='تایید رمز عبور', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                            'placeholder': 'Retype your password'}))

    def clean(self):  # overrides built-in clean function to check entry password inputs
        cd = super().clean()
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords must match')

    def clean_phone_number(self): # validates phone number input with database
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('Phone Number already exists')
        return phone_number

    def clean_email(self): # validates email input with database
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists')
        return email


class OtpCodeForm(forms.Form):  # creates integer input to get code from user
    OtpCode = forms.IntegerField(label='کد یکبار مصرف', widget=forms.NumberInput(attrs={'class': 'form-control',
                                                                            'placeholder': 'Enter your Otp Code here'}))


class UserLoginForm(forms.Form): # creates inputs to get info from user to log in
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs={'class': 'form-control'}))