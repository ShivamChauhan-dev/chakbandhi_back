from django.db import models
from django.utils import timezone


class AppBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    deleted = models.BooleanField(default=False, editable=False)
    modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.modified = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.force_delete()

    def force_delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)


class TitleModelMixin(models.Model):
    max_length = 50
    unique = True
    title = models.CharField(max_length=max_length, unique=unique)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
