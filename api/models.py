import os

from django.contrib.auth.models import User
from django.db import models
from backend_django_tesis.settings import BASE_DIR


# Create your models here.

class WRFoutFile(models.Model):
    name = models.TextField(unique=True)
    path_file = models.FileField(upload_to="wrfout_files/", blank=True, null=True)
    path_string = models.TextField(blank=True, null=True)
    size = models.FloatField()

    @classmethod
    def refresh_list_of_files(cls):
        # files = os.scandir(f"{BASE_DIR}/wrfout_files/")
        # for file in files:
        #     if not cls.objects.filter(name=slugify(file.name)).first() and not cls.objects.filter(name=file.name).first():
        #         try:
        #             cls.objects.create(
        #                 name=slugify(file.name),
        #                 path_string=file.path,
        #                 size=round(float(file.stat().st_size)/1000000, 2)
        #             )
        #         except:
        #             pass
        for file in cls.objects.all():
            for root, dirs, files in os.walk(f"{BASE_DIR}/wrfout_files/"):
                if not file.name in files:
                    file.delete()

    @classmethod
    def get_used_space(cls):
        used_space = 0
        for file in cls.objects.all():
            used_space = used_space + file.size

        used_space = round(used_space / 1000, 2)
        return used_space
