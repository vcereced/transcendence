from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    # path('boxes/', csrf_exempt(views.BoxList.as_view())),
    # path('boxes/<int:pk>/', csrf_exempt(views.BoxDetail.as_view())),
]

urlpatterns = format_suffix_patterns(urlpatterns)
