from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # path('', csrf_exempt(views.UserList.as_view())),
    # path('<int:pk>/', csrf_exempt(views.UserDetail.as_view())),
]

urlpatterns = format_suffix_patterns(urlpatterns)
