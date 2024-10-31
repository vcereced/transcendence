from rest_framework import serializers
# from .models import Box

# ORDER_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('ACCEPTED', 'Accepted'),
#         ('DENIED', 'Denied'),
#     ]

# class BoxSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Box
#         fields = ['id', 'units', 'date']

# class OrderSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     units = serializers.IntegerField()
#     status = serializers.ChoiceField(choices=ORDER_STATUS_CHOICES)
#     date = serializers.DateTimeField()
