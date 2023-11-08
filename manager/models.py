from django.db import models

# Create your models here.


class Content(models.Model):
    site_title = models.TextField(blank=True)
    icon = models.TextField(blank=True)
    favicon = models.TextField(blank=True)
    home_content = models.TextField(blank=True)
    card_diagnostics = models.TextField(blank=True)
    card_my_diagnostics = models.TextField(blank=True)
    help_content = models.TextField(blank=True)
    server_space = models.FloatField(default=0)

