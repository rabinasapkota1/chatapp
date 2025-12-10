from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

# Import your existing encryption utilities
from chat_app.utils.crypto import encrypt, decrypt


# 🔥 Your original model + added online/offline support
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Existing fields (unchanged)
    name = models.CharField(max_length=200)
    secret_encrypted = models.TextField(blank=True, null=True)

    # ✅ New field for online/offline tracking
    last_seen = models.DateTimeField(default=timezone.now)

    # Existing encrypted property (unchanged)
    @property
    def secret(self):
        if not self.secret_encrypted:
            return None
        return decrypt(self.secret_encrypted).decode("utf-8")

    @secret.setter
    def secret(self, value):
        self.secret_encrypted = encrypt(value)

    # ✅ New online/offline detection
    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timedelta(minutes=2)


# Automatically create Profile for new User (unchanged)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# Optional helper to update last_seen manually
def update_last_seen(user):
    user.profile.last_seen = timezone.now()
    user.profile.save(update_fields=["last_seen"])
