from django.db import models


# ORDER_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('ACCEPTED', 'Accepted'),
#         ('DENIED', 'Denied'),
#     ]

# class User(models.Model):
#     id = models.AutoField(primary_key=True)
#     units = models.IntegerField()
#     status = models.CharField(
#         max_length=100,
#         choices=ORDER_STATUS_CHOICES,
#         default='PENDING',
#     )
#     date = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         usering = ['date']


#     def __str__(self):
#         return f"User {self.id} ({self.status}) - {self.units} units"
