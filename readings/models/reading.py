from django.db import models
from django.db.models import DateTimeField, CharField, ForeignKey, DecimalField, TextField, BooleanField, IntegerField
from readings.models.flow_file import FlowFile

class MeterReading(models.Model):
    

    file_name = models.ForeignKey(
        FlowFile,
        on_delete=models.CASCADE
    )

    mpan_core = CharField(max_length=255, null=True, blank=True, verbose_name="MPAN Core")
    bsc_validation_status = CharField(max_length=255, null=True, blank=True, verbose_name="BSC Validation Status")
    site_visit_check_code = CharField(max_length=255, null=True, blank=True, verbose_name="Site Visit Check Code")
    additional_information =  TextField(blank=True, null=True, verbose_name="Additional Information")
    meter_id = CharField(max_length=255, null=True, blank=True, verbose_name="Meter Id (Serial Number)")
    reading_type = CharField(max_length=255, null=True, blank=True, verbose_name="Reading Type")
    meter_register_id = CharField(max_length=255, null=True, blank=True, verbose_name="Meter Register Id")
    reading_date_time = DateTimeField(null=True, blank=True,  verbose_name="Reading Date & Time")
    register_reading = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Register Reading")
    md_reset_date_time = DateTimeField(null=True, blank=True, verbose_name="MD Reset Date & Time")
    number_of_md_resets = IntegerField(null=True, blank=True, verbose_name="Number of MD Resets")
    meter_reading_flag = BooleanField(null=True, default=None, verbose_name="Meter Reading Flag")
    reading_method = CharField(max_length=255, null=True, blank=True, verbose_name="Reading Method")
    meter_reading_reason_code = CharField(max_length=255, null=True, blank=True, verbose_name="Meter Reading Reason Code")
    meter_reading_status = CharField(max_length=255, null=True, blank=True, verbose_name="Meter Reading Status")
    created = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        verbose_name = "Meter Reading"
        ordering = ("-id",)
