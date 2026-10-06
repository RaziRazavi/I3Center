import django_filters
from django import forms
from products.models import Brand, Material


class ProductsFilter(django_filters.FilterSet):
    PRICE_CHOICES = (
        ('1','ارزان ترین'),
        ('2','گران ترین'),
    )  # creates static choices
    LIKE_CHOICES = (
        ('1','کم ترین'),
        ('2','بیش ترین'),
    ) # creates static choices
    DATE_CHOICES = (
        ('1', 'قدیمی ترین'),
        ('2', 'جدید ترین'),
    ) # creates static choices
    BOOLEAN_CHOICES = (
        (True, 'بله'),
        (False, 'خیر'),
    )  # creates static choices

    min_price = django_filters.NumberFilter(field_name='start_price', lookup_expr='gte', label='حداقل قیمت',
                                            widget=forms.NumberInput(attrs={'class': 'form-control'})) # filters range prices
    max_price = django_filters.NumberFilter(field_name='start_price', lookup_expr='lte', label='حداکثر قیمت',
                                            widget=forms.NumberInput(attrs={'class': 'form-control'})) # filters range prices
    sort_price = django_filters.ChoiceFilter(choices=PRICE_CHOICES, label='قیمت', method='sort_prices',
                                        widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on prices
    sort_like = django_filters.ChoiceFilter(choices=LIKE_CHOICES, label='محبوبیت', method='sort_likes',
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on likes count
    sort_date = django_filters.ChoiceFilter(choices=DATE_CHOICES, label='تاریخ ایجاد',method='sort_dates',
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on new/oldest
    available = django_filters.ChoiceFilter(field_name='available', label='موجود',
              choices= BOOLEAN_CHOICES, widget=forms.Select(attrs={'class': 'form-control'})) # filters available ones
    discount = django_filters.ChoiceFilter(field_name='has_discount', label='تخفیف',
                choices=BOOLEAN_CHOICES, widget=forms.Select(attrs={'class': 'form-control'})) # filters ones with discount
    sort_view = django_filters.ChoiceFilter(choices=LIKE_CHOICES, label='بازدید',method='sort_views',
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on views count
    sort_sale = django_filters.ChoiceFilter(choices=LIKE_CHOICES, label='فروش',method='sort_sales',
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on sales count
    brand = django_filters.ModelMultipleChoiceFilter(field_name='brand', queryset=Brand.objects.all(), label='برند',
                                                     widget=forms.CheckboxSelectMultiple()) # filters brands
    material = django_filters.ModelMultipleChoiceFilter(field_name='material', queryset=Material.objects.all(),
                                                        label='جنس', widget=forms.CheckboxSelectMultiple()) # filters materials

    def sort_prices(self, queryset, name, value):  # # gets static value and base on that sorts taken data from database
        sort = 'start_price' if value == '1' else '-start_price'
        return queryset.order_by(sort)

    def sort_dates(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'created_at' if value == '1' else '-created_at'
        return queryset.order_by(sort)

    def sort_likes(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'favorites_count' if value == '1' else '-favorites_count'
        return queryset.order_by(sort)

    def sort_views(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'views_count' if value == '1' else '-views_count'
        return queryset.order_by(sort)

    def sort_sales(self, queryset, name, value): # gets static value and base on that sorts taken data from database
            sort = 'sales_count' if value == '1' else '-sales_count'
            return queryset.order_by(sort)
