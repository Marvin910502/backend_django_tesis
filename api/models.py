import base64
import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from backend_django_tesis.settings import BASE_DIR


# Create your models here.

class WRFoutFileList(models.Model):
    name = models.CharField(max_length=150)
    path = models.TextField()
    size = models.FloatField()

    @classmethod
    def refresh_list_of_files(cls):
        for file in os.scandir(f"{BASE_DIR}/wrfout_files/"):
            if not cls.objects.filter(name=file.name).first():
                cls.objects.create(
                    name=file.name,
                    path=file.path,
                    size=file.__sizeof__()
                )
