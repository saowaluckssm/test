
from django.contrib import admin
from .models import FlowFile, MeterReading

@admin.register(FlowFile)
class FlowFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_at')


@admin.register(MeterReading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = (
        'mpan_core',
        'meter_id',
        'reading_date_time',
        'register_reading',
        'meter_register_id',
        'file_name',
        'meter_reading_flag',
        'number_of_md_resets',
        'reading_method',
        'created',
    )
    search_fields = (
        'mpan_core',
        'meter_id',
        'meter_register_id',
        'file_name__file_name',
    )
    list_filter = (
        'meter_reading_flag',
        'number_of_md_resets',
        'reading_method',
        'created',
    )



