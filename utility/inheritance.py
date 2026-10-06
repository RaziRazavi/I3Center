from django.db import models
import jdatetime
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def created_at_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=timezone.localtime(self.created_at)).strftime('%Y-%m-%d %H:%M')

    @property
    def updated_at_jalali(self):
        return jdatetime.datetime.fromgregorian(datetime=timezone.localtime(self.updated_at)).strftime('%Y-%m-%d %H:%M')
