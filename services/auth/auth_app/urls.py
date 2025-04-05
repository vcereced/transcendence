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
    path('playersList', views.playersList_view, name='playersList'),
    path('isFriendShip', views.isFriendShip_view, name='isFriendShip'),
    path('friendShip/<str:action>', views.friendShip_view, name='friendShip'),

    path('updatePictureUrl', views.updatePictureUrl_view, name='updatePictureUrl'),
    path('updateName', views.updateName_view, name='updateName'),
    path('updatePassword', views.updatePassword_view, name='updatePassword'),
    path('dataUser', views.dataUser_view, name='dataUser'),

]