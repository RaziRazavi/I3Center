from django.urls import path
from products import views


app_name = 'products'


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductView.as_view(), name='view'),
    path('products/<int:pk>/<str:slug>/', views.ProductView.as_view(), name='view_from_category'),
    path('product/details/<int:pk>/<str:slug>/', views.ProductDetailsView.as_view(), name='details'),
    path('category/', views.CategoryView.as_view(), name='category_view'),
    path('category/<int:pk>/<str:slug>/', views.CategoryView.as_view(), name='category_sub'),
    path('products/like/<int:pk>/', views.ProductLikeView.as_view(), name='product_like'),
    path('products/comment-like/<int:pk>/', views.CommentLikeView.as_view(), name='comment_like'),
    path('products/comment-dislike/<int:pk>/', views.CommentDislikeView.as_view(), name='comment_dislike'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
]