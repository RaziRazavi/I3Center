from django import forms
from products.models import Comment, ContactUs


class CommentForm(forms.ModelForm): #creates input base on a field from a table in database and inherits its features
    class Meta:
        model = Comment  # gets from this table
        fields = ('body',)  # this field
        widgets = {
            'body': forms.Textarea(attrs={'class':'form-control'}),
        }  # adds bootstrap class and declare their input types


class SearchForm(forms.Form):  # creates search input
    search = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'type': 'search',
                'placeholder': 'محصول خود را اینجا جستجو کنید ...',}), required=False)



class ContactUsForm(forms.ModelForm): #creates inputs base on some fields from a table in database & inherits features
    class Meta:
        model = ContactUs  # gets from this table
        fields = ('name', 'phone_number', 'email', 'subject', 'message') # these fields
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'phone_number': forms.NumberInput(attrs={'class':'form-control'},),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'subject': forms.TextInput(attrs={'class':'form-control'}),
            'message': forms.Textarea(attrs={'class':'form-control'}),
        } # adds bootstrap class and declare their input types