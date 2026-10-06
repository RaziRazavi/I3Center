from django.urls import path
from accounts import views


app_name = 'accounts'


urlpatterns = [
    path('user-register/', views.UserRegisterView.as_view(), name='user_register'),
    path('user-register-verify/', views.UserRegisterVerifyView.as_view(), name='user_register_verify'),
    path('user-password-reset/', views.UserPasswordResetView.as_view(), name='user_password_reset'),
    path('user-password-reset-done/', views.UserPasswordResetDoneView.as_view(), name='user_password_reset_done'),
    path('user-password-reset-confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='user_password_reset_confirm'),
    path('user-password-reset-complete/', views.UserPasswordResetCompleteView.as_view(), name='user_password_reset_complete'),
    path('user-login/', views.UserLoginView.as_view(), name='user_login'),
    path('user-logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('user-login-verify/', views.UserLoginVerifyView.as_view(), name='user_login_verify'),
    path('user-password-change/', views.UserPasswordChangeView.as_view(), name='user_password_change'),
    path('user-password-change-done/', views.UserPasswordChangeDoneView.as_view(), name='user_password_change_done'),
]