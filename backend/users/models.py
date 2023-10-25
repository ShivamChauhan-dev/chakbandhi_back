from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from drone_destination.base_model import AppBaseModel


class OTPSourceTypes(models.IntegerChoices):
    Phone = 1, "Phone"
    Email = 2, "Email"
    VOICE = 3, "Voice"


class DDUser(AbstractUser):
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(_("email address"), blank=True, null=True)

    def __str__(self):
        return f"{self.username}({self.pk})-{''.join([f'{group}' for group in self.groups.all()])}"


class CreatorMixin(models.Model):
    creator = models.ForeignKey(DDUser, on_delete=models.CASCADE, editable=False)
    modified_by = models.ForeignKey(
        DDUser, on_delete=models.SET_NULL, editable=False, default=None, null=True, related_name='+'
    )

    class Meta:
        abstract = True


class OTPLog(CreatorMixin, AppBaseModel):
    token = models.UUIDField(editable=False)
    code = models.PositiveIntegerField()
    sent_on = models.PositiveSmallIntegerField(choices=OTPSourceTypes.choices, editable=False)
    is_utilized = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.sent_on.__str__()


class DEVICES(models.IntegerChoices):
    ANDROID = 1, "android"
    IOS = 2, "ios"
    MACOS = 3, "macos"
    WINDOWS = 4, "windows"


class FCMTokens(CreatorMixin, AppBaseModel):
    token = models.TextField(null=False, blank=False)
    device = models.PositiveSmallIntegerField(choices=DEVICES.choices)
