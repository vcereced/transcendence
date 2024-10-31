from .models import Box
from .serializers import BoxSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics



# class BoxList(generics.ListCreateAPIView):
#     queryset = Box.objects.all()
#     serializer_class = BoxSerializer


# class BoxDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Box.objects.all()
#     serializer_class = BoxSerializer