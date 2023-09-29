import base64
import uuid

from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class UserToken(models.Model):
    token = models.CharField(max_length=172, db_index=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    @property
    def authorization_bearer(self):
        return {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def generate_token():
        part_1 = uuid.uuid4().__str__()
        part_2 = uuid.uuid4().__str__()
        part_3 = uuid.uuid4().__str__()
        part_4 = uuid.uuid4().__str__()
        token = base64.b64encode(
            f"{part_1}{part_2}{part_3}{part_4}".replace("-", "").encode()
        ).decode()
        return token

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.token = self.generate_token()
        super(UserToken, self).save(*args, **kwargs)

