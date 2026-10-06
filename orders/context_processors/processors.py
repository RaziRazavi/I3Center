from orders.cart import Cart
from products.forms import SearchForm
from products.models import Category


def cart_processor(request):
    return {
        'cart': Cart(request),
        'search_form': SearchForm(),
        'departments': Category.objects.filter(is_parent=True).prefetch_related('sub_categories'),
    }