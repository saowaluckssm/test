
from datetime import datetime
import os
import logging
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from readings.models import FlowFile, MeterReading

logger = logging.getLogger(__name__)

# Define file inbox and destination for ingested files
file_inbox_path = settings.BASE_DIR / 'readings/file_inbox/'

# ----------- Parsing a 030 Record Line (Flow Reading) ------------
def parse_flow_reading(line):
    """Parse a '030' line into a dictionary for creating a MeterReading."""
    try:
        reading_date_time = timezone.make_aware(datetime.strptime(line[2], '%Y%m%d%H%M%S'))
        register_reading = Decimal(line[3])
    except (ValueError, IndexError, InvalidOperation) as e:
        logger.warning(f"Skipping invalid reading line: {line} - {e}")
        return None

    # Optional MD Reset Date
    md_reset_date_time = None
    if len(line) > 4 and line[4]:
        try:
            md_reset_date_time = timezone.make_aware(datetime.strptime(line[4], '%Y%m%d%H%M%S'))
        except ValueError:
            pass

    # Build reading dictionary
    return {
        'reading_date_time': reading_date_time,
        'register_reading': register_reading,
        'md_reset_date_time': md_reset_date_time,
        'number_of_md_resets': line[5] if len(line) > 5 and line[5] else None,
        'meter_reading_flag': line[6] == 'T' if len(line) > 6 else False,
        'reading_method': line[7] if len(line) > 7 else None,
        'meter_register_id': line[1] if len(line) > 1 else None,
    }

# ----------- Creating a MeterReading Object ----------------------
def create_meter_reading(mpan, meter_type, reading_data, file_obj, ingestion_time):
    """Construct a MeterReading instance from parsed data."""
    return MeterReading(
        mpan_core=mpan[1],
        meter_id=meter_type[1],
        file_name=file_obj,
        created=ingestion_time,
        **reading_data,
    )

# ----------- Main File Line Processing ---------------------------
def process_file_lines(lines, ingestion_time, file_name):
    """
    Parse the file content and generate MeterReading objects.
    Groups each MPAN (026), meter ID (028), and all related 030 lines.
    """
    readings = []
    mpan, meter_type = [], []
    register_lines = []

    for line in lines:
        line = line.strip().split('|')

        # Capture new MPAN block
        if line[0] == '026':
            # Flush previous MPAN block
            if mpan and meter_type and register_lines:
                file_obj = FlowFile.objects.get(file_name=file_name)
                for register_line in register_lines:
                    reading_data = parse_flow_reading(register_line)
                    if reading_data:
                        readings.append(
                            create_meter_reading(mpan, meter_type, reading_data, file_obj, ingestion_time)
                        )
                register_lines = []  # Reset for next block
            mpan = line

        elif line[0] == '028':
            meter_type = line
        elif line[0] == '030':
            register_lines.append(line)
        elif line[0] == 'ZPT':
            continue  # Footer — nothing to do

    return readings

# ----------- Handling Entire File -------------------------------
def handle_file_ingestion(file_lines, ingestion_time, file_name):
    """Main entry point for ingesting a file's data into the database."""
    if FlowFile.objects.filter(file_name=file_name).exists():
        logger.info(f'File "{file_name}" already ingested.')
        return

    try:
        # Create FlowFile record (for tracking ingestion)
        FlowFile.objects.create(
            file_name=file_name,
            header=file_lines[0],
            footer=file_lines[-1],
            uploaded_at=ingestion_time
        )

        # Generate and save all MeterReading records
        readings = process_file_lines(file_lines, ingestion_time, file_name)
        MeterReading.objects.bulk_create(readings)

        logger.info(f'File "{file_name}" successfully ingested.')

    except Exception as e:
        logger.error(f'Error processing file "{file_name}": {e}', exc_info=True)

# ----------- Django Management Command --------------------------
class Command(BaseCommand):
    help = 'Ingest .uff meter reading files.'

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs='?', help='Optional specific file to process')

    def handle(self, *args, **options):
        ingestion_time = timezone.now()
        files = self.get_files_to_process(options.get('file_name'))

        for file_name in files:
            file_path = file_inbox_path / file_name
            try:
                with open(file_path, 'r') as f:
                    file_lines = list(f)
                handle_file_ingestion(file_lines, ingestion_time, file_name)
            except Exception as e:
                logger.error(f"Failed to read file {file_name}: {e}", exc_info=True)

    def get_files_to_process(self, file_name):
        """Select which .uff files to process (single or all)."""
        if file_name:
            return [file_name]
        return [f for f in os.listdir(file_inbox_path) if f.endswith('.uff')]
