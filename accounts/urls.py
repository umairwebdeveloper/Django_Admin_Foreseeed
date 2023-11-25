# from django.urls import path
# from .views import ResetPasswordView, mydata
# from django.contrib.auth import views as auth_views


# urlpatterns = [
#     path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
#     path('password-reset-confirm/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
#          name='password_reset_confirm'),
#     path('password-reset-complete/',
#          auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
#          name='password_reset_complete'),
#     path('test/', mydata, name='test    ')
# ]

# from django.contrib.auth import views
# from django.urls import path 

# urlpatterns = [
#    path('login/', views.LoginView.as_view(), name='login'), 
#    path('logout/', views.LogoutView.as_view(), name='logout'),
   
#    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
#    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
#    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
#    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

#    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
#    path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
# ]

from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    
    path('' , Home , name="home"),
    # path('login/' , Login , name="login"),
    path('register/' , Register , name="register"),
    path('forget-password/' , ForgetPassword , name="forget_password"),
    path('change-password/<token>/' , ChangePassword , name="change_password"),
    path('logout/' , Logout , name="logout"),
    
    
    
 
]