from django import forms
from posts.models import PostComment


class PostCommentForm(forms.ModelForm): #creates input base on a field from a table in database and inherits its features
    class Meta:
        model = PostComment  # gets from this table
        fields = ('body',) # this field
        widgets = {
            'body': forms.Textarea(attrs={'class':'form-control'}),
        } # adds bootstrap classes and declare their input types


class PostSearchForm(forms.Form):  # creates a search input
    search = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'form-control', 'type': 'search',
                'placeholder': 'مقاله خود را اینجا جستجو کنید ...',}), required=False)
