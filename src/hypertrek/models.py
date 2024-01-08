from hypergen.imports import context

from django.db import models
from django.conf import settings

class TrekState(models.Model):
    added = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+',
                                 on_delete=models.PROTECT, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+',
                                   on_delete=models.PROTECT, editable=False)

    uuid = models.UUIDField(editable=False)
    value = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        if "request" in context and context["request"].user.is_authenticated:
            if self.pk is None:
                self.added_by = context.request.user

            self.updated_by = context.request.user

        super().save(*args, **kwargs)
