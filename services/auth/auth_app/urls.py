from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


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
    path('logout', views.logout_view, name='logout'),
    path('user/<str:username>', views.UserDetail.as_view(), name='user_detail'),
	path('user/id/<int:pk>', views.UserDetailById.as_view(), name='user_detail_by_id'),
    path('upload-profile-pic', views.upload_profile_pic_view, name='upload_profile_pic'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)