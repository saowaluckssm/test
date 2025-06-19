
# from datetime import datetime
# import os
# import logging
# import shutil
# from django.conf import settings
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from readings.models import FlowFile, MeterReading
# from decimal import Decimal, InvalidOperation
# import traceback


# logger = logging.getLogger(__name__)

# file_inbox_path = settings.BASE_DIR / 'readings/file_inbox/'
# ingested_files_path = settings.BASE_DIR / 'readings/file_inbox/ingested_files/'



# def parse_flow_reading(line_listified):
#     """Parse a 030 line into MeterReading fields."""
#     try:
#         reading_date_time = timezone.make_aware(
#             datetime.strptime(line_listified[2], '%Y%m%d%H%M%S')
#         )
#         register_reading = Decimal(line_listified[3])
#     except (ValueError, IndexError, InvalidOperation) as e:
#         logger.warning(f"Invalid reading line: {line_listified} - {e}")
#         return None  # Skip this reading

#     md_reset_date_time = None
#     if line_listified[4]:
#         try:
#             md_reset_date_time = timezone.make_aware(
#                 datetime.strptime(line_listified[4], '%Y%m%d%H%M%S')
#             )
#         except ValueError:
#             md_reset_date_time = None

#     return {
#         'reading_date_time': reading_date_time,
#         'register_reading': register_reading,
#         'md_reset_date_time': md_reset_date_time,
#         'number_of_md_resets': line_listified[5] if line_listified[5] else None,
#         'meter_reading_flag': line_listified[6] == 'T',
#         'reading_method': line_listified[7] if len(line_listified) > 7 else None,
#     }


# def create_meter_reading_object(mpan_cores, meter_reading_type, register_readings, file_name, ingestion_time):
#     """Create a MeterReading object from parsed data."""
#     file_obj = FlowFile.objects.get(file_name=file_name)
#     return MeterReading(
#         mpan_core=mpan_cores[1],
#         meter_id=meter_reading_type[1],
#         # meter_register_id=register_readings[1],
#         file_name=file_obj,
#         created=ingestion_time,
#         **register_readings,
#     )


# def process_file_lines(file_listified, ingestion_time, file_name):
#     """Process file lines into a list of MeterReading objects."""
#     object_list = []
#     mpan_cores, meter_reading_type = [], []
#     register_readings_list = []
#     prev_record_type = '000'

#     for line in file_listified:
#         line_listified = line.strip().split('|')

#         # Skip header
#         if line_listified[0] > '999' and not mpan_cores:
#             continue

#         # Flush previous record set if a new set starts or footer appears
#         if line_listified[0] in ('026', 'ZPT') and mpan_cores and meter_reading_type and register_readings_list:
#             for register_readings in register_readings_list:
#                 flow_readings_parsed = parse_flow_reading(register_readings)
#                 flow_readings_parsed['meter_register_id'] = register_readings[1]
#                 new_object = create_meter_reading_object(
#                     mpan_cores, meter_reading_type, flow_readings_parsed, file_name, ingestion_time
#                 )
#                 object_list.append(new_object)
#             register_readings_list = []  # Reset for next block

#         # Record types
#         if line_listified[0] == '026':
#             mpan_cores = line_listified
#         elif line_listified[0] == '028':
#             meter_reading_type = line_listified
#         elif line_listified[0] == '030':
#             register_readings_list.append(line_listified)

#         prev_record_type = line_listified[0]

#     return object_list


# def handle_file_ingestion(file_listified, ingestion_time, file_name):
#     """Handle the ingestion process for a given file."""
#     try:
#         # Ensure the file has not been ingested before
#         if FlowFile.objects.filter(file_name=file_name).exists():
#             logger.info(f'The file "{file_name}" has already been ingested.')
#             return

#         # Insert file record into the Files table
#         FlowFile.objects.create(
#             file_name=file_name,
#             header=file_listified[0],
#             footer=file_listified[-1],
#             uploaded_at=ingestion_time
#         )

#         # Process lines and create RegisterReading objects
#         object_list = process_file_lines(file_listified, ingestion_time, file_name)

#         # Bulk insert MeterReading
#         MeterReading.objects.bulk_create(object_list)
#         logger.info(f'File "{file_name}" successfully ingested.')

#         # Move the file to the ingested folder
#         # os.rename(file_inbox_path / file_name, ingested_files_path / file_name)
#         # shutil.move(file_inbox_path / file_name, ingested_files_path / file_name)

   

#     except Exception as e:
#         logger.error(f'Error processing file "{file_name}": {e}')
#         logger.error(traceback.format_exc())


# class Command(BaseCommand):
#     # help = 'Ingest meter reading files into the system.'

#     def add_arguments(self, parser):
#         parser.add_argument('file_name', nargs='?', default=None, help="File name to process")

#     def handle(self, *args, **options):
#         ingestion_time = timezone.now()
#         uff_files = self.get_files_to_process(options)

#         for uff_file_name in uff_files:
#             file_in_inbox = file_inbox_path / uff_file_name
#             try:
#                 with open(file_in_inbox, 'r') as file:
#                     file_listified = list(file)
#             except Exception as e:
#                 logger.error(f"Error reading file {uff_file_name}: {e}")
#                 continue

#             handle_file_ingestion(file_listified, ingestion_time, uff_file_name)

#     def get_files_to_process(self, options):
#         """Determine which files to process, based on command arguments."""
#         paths = os.listdir(file_inbox_path)
#         uff_files = [path for path in paths if path.endswith('.uff')]

#         if options.get('file_name'):
#             uff_files = [options['file_name']]
#         return uff_files

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
