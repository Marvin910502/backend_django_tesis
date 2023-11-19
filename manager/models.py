from django.db import models

# Create your models here.


class Content(models.Model):
    site_title = models.TextField(blank=True)
    server_space = models.FloatField(default=0)
    icon = models.FileField(upload_to="static/icons/", blank=True, null=True)
    icon_name = models.CharField(max_length=200, blank=True, null=True)
    favicon = models.FileField(upload_to="static/icons/", blank=True, null=True)
    favicon_name = models.CharField(max_length=200, blank=True, null=True)
    home_top_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    home_top_image_name = models.CharField(max_length=200, blank=True, null=True)
    card_diagnostics_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    card_diagnostics_image_name = models.CharField(max_length=200, blank=True, null=True)
    card_my_diagnostics_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    card_my_diagnostics_image_name = models.CharField(max_length=200, blank=True, null=True)
    home_content = models.TextField(blank=True)
    card_diagnostics = models.TextField(blank=True)
    card_my_diagnostics = models.TextField(blank=True)
    help_content = models.TextField(blank=True)


class Logs(models.Model):
    action = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    ip = models.CharField(max_length=30, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    status_code = models.CharField(max_length=3, blank=True, null=True)
    message = models.CharField(max_length=200, blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)

