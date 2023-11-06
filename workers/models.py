import uuid

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Worker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=150, default='Visitante')
    name = models.CharField(max_length=50, null=True, blank=True)
    last_names = models.CharField(max_length=100, null=True, blank=True)
    isAdmin = models.BooleanField(default=False)
    isGuess = models.BooleanField(default=False)
    isManager = models.BooleanField(default=False)
    uuid = models.CharField('UUID', max_length=36, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.uuid = uuid.uuid4().__str__()
        super(Worker, self).save(*args, **kwargs)


class Diagnostic(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    geojson = models.TextField()
    diagnostic = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    polygons = models.IntegerField()
    file_name = models.CharField(max_length=100)

