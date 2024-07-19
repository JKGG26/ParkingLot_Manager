from django.contrib.auth.models import User
from django.db import models


class BlackListTokenAccess(models.Model):
    token = models.TextField()
    user_id = models.ForeignKey(
        User,                  # Model (Table) to set foreign key relation
        null=False,                  # Allow null values in this field
        blank=False,                 # Allow blank values in this field
        on_delete=models.CASCADE    # If a User is deleted, all related inactive tokens too
    )
    added_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
