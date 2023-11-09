from django.db import models

# Create your models here.


class Content(models.Model):
    site_title = models.TextField(blank=True)
    icon = models.FileField(upload_to="static/icons/", blank=True, null=True)
    favicon = models.FileField(upload_to="static/icons/", blank=True, null=True)
    home_top_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    card_diagnostics_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    card_my_diagnostics_image = models.FileField(upload_to="static/images/", blank=True, null=True)
    home_content = models.TextField(blank=True)
    card_diagnostics = models.TextField(blank=True)
    card_my_diagnostics = models.TextField(blank=True)
    help_content = models.TextField(blank=True)
    server_space = models.FloatField(default=0)

