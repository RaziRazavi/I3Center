import django_filters
from django import forms


class PostFilters(django_filters.FilterSet):  # gets products and runs some filters on them
    STATUS_CHOICES = (
        ('1', 'کم ترین'),
        ('2', 'بیش ترین'),
    )  # static choices
    DATA_CHOICES = (
        ('1', 'قدیمی ترین'),
        ('2', 'جدید ترین'),
    )  # static choices

    sort_view = django_filters.ChoiceFilter(label='تعداد بازدید', method='views_count', choices=STATUS_CHOICES,
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on views count
    sort_like = django_filters.ChoiceFilter(label='تعداد لایک', method='likes_count', choices=STATUS_CHOICES,
                                            widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on likes count
    sort_comment = django_filters.ChoiceFilter(label='تعداد کامنت', method='comments_count', choices=STATUS_CHOICES,
                                               widget=forms.Select(attrs={'class': 'form-control'})) #sorts base on comments count
    sort_data = django_filters.ChoiceFilter(label='تاریخ ایجاد', choices=DATA_CHOICES, method='data_sort',
                                               widget=forms.Select(attrs={'class': 'form-control'})) # sorts base on new / oldest

    def views_count(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'views_count' if value == '1' else '-views_count'
        return queryset.order_by(sort)

    def likes_count(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'likes_count' if value == '1' else '-likes_count'
        return queryset.order_by(sort)

    def comments_count(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'comments_count' if value == '1' else '-comments_count'
        return queryset.order_by(sort)

    def data_sort(self, queryset, name, value): # gets static value and base on that sorts taken data from database
        sort = 'created_at' if value == '1' else '-created_at'
        return queryset.order_by(sort)