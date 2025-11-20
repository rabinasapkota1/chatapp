from django.db import models

# Create your models here.
# users/models.py (excerpt)
from chat_app.utils.crypto import encrypt, decrypt

class Profile(models.Model):
    name = models.CharField(max_length=200)
    secret_encrypted = models.TextField(blank=True, null=True)

    @property
    def secret(self):
        if not self.secret_encrypted:
            return None
        return decrypt(self.secret_encrypted).decode("utf-8")

    @secret.setter
    def secret(self, value):
        # value can be str
        self.secret_encrypted = encrypt(value)
