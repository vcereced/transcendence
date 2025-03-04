from django.urls import path, include
from . import views


urlpatterns = [
    path('login', views.login_api_view, name='login'),
	path('register', views.register_view, name='register'),
    path('validateToken', views.validate_token_view, name='validate_token'),
    path('refreshToken', views.refresh_token_view, name='refresh_token'),
    #path('verify_otp', views.verify_otp_view, name='refresh_token'),
    path('verify_email_otp', views.verify_email_otp_view, name='refresh_token'),
   # path('login_qr', views.login_qr_view, name='refresh_token'),
    path('login_email', views.login_email_view, name='refresh_token'),
]