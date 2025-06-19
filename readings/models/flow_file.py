from django.db import models
from django.db.models import TextField, DateTimeField, CharField, ForeignKey


class FlowFile(models.Model):
    file_name = CharField(max_length=255, null=True, blank=True, verbose_name="File Name" )
    header = CharField(max_length=255,  null=True, blank=True, verbose_name="Header")
    footer = CharField(max_length=255,   null=True, blank=True, verbose_name="Footer")
    uploaded_at = DateTimeField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "Flow File"
        verbose_name_plural = "Flow Files"
        ordering = ("-id",)