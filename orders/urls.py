from django.urls import path
from orders import views


app_name = 'orders'


urlpatterns = [
    path('cart/view/', views.CartView.as_view(), name='cart_view'),
    path('cart/update/<int:pk>/', views.UpdateCartQuantityView.as_view(), name='cart_update'),
    path('cart/add/<int:pk>/', views.AddToCartView.as_view(), name='cart_add'),
    path('form/', views.OrderFormView.as_view(), name='order_form'),
    path('modify/<int:id>/', views.OrderModifyView.as_view(), name='order_modify'),
    path('update-quantity/<int:id>/', views.UpdateQuantityView.as_view(), name='update_quantity'),
    path('view/', views.OrderView.as_view(), name='order_view'),
    path('details/<int:id>/', views.OrderDetailView.as_view(), name='order_details'),
    path('pay/<int:id>/', views.OrderPayView.as_view(), name='order_pay'),
    path('zp-request/<int:id>/', views.PaymentRequestView.as_view(), name='zp_request'),
    path('zp-verify/', views.PaymentVerifyView.as_view(), name='zp_verify'),
]