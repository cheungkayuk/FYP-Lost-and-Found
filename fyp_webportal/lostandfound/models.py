from django.db import models

# Create your models here.

class LostFoundItem(models.Model):
    classname = models.CharField(max_length=200)
    checkpoint = models.CharField(max_length=10)
    direction = models.PositiveIntegerField()
    detectedTime = models.DateTimeField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.classname
