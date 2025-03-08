from django.urls import path, include
from . import views


urlpatterns = [
    path('login', views.login_api_view, name='login'),
	path('register', views.register_view, name='register'),
    path('validateToken', views.validate_token_view, name='validate_token'),
    path('refreshToken', views.refresh_token_view, name='refresh_token'),
    path('verify_email_otp_register', views.verify_email_otp_register_view, name='verify_email_otp'),
    path('resend_otp', views.resend_otp_view, name='resend_otp'),
    path('verify_email_otp_login', views.verify_email_otp_login_view, name='login_email'),
]