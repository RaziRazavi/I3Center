from django.urls import path
from posts import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostView.as_view(), name='view'),
    path('category/<int:pk>/<str:slug>/', views.PostView.as_view(), name='view_from_category'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('category/<int:category_pk>/<str:category_slug>/<int:post_pk>/<str:post_slug>/',
         views.PostDetailsView.as_view(), name='details'),
    path('post-love/<int:pk>/', views.PostLoveView.as_view(), name='post_love'),
    path('comment-love/<int:pk>/', views.PostCommentLoveView.as_view(), name='comment_love'),
    path('comment-hate/<int:pk>/', views.PostCommentHateView.as_view(), name='comment_hate'),
]
