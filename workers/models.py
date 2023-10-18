from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Worker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=50)
    last_names = models.CharField(max_length=100)
    isAdmin = models.BooleanField(default=False)
    isGuess = models.BooleanField(default=False)
    isManager = models.BooleanField(default=False)
