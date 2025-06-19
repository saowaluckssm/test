
from django.test import TestCase
from readings.models import MeterReading, FlowFile
from django.utils import timezone
from readings.management.commands.import_d0010 import handle_file_ingestion
from decimal import Decimal

class SimpleImportTests(TestCase):
    def setUp(self):
        self.fake_file_name = "test_file.uff"
        self.ingestion_time = timezone.now()

        # Clean up before running the test
        FlowFile.objects.filter(file_name=self.fake_file_name).delete()

        self.file_lines = [
            "026|MPANCORE123456789\n",
            "028|METERID123\n",
            "030|X|20240101000000|123.45|20231231000000|0|T|AUTO\n",
            "ZPT|END\n"
        ]

    def test_file_ingests_meter_reading(self):
        handle_file_ingestion(self.file_lines, self.ingestion_time, self.fake_file_name)

        self.assertTrue(FlowFile.objects.filter(file_name=self.fake_file_name).exists())
        self.assertEqual(MeterReading.objects.count(), 1)
        reading = MeterReading.objects.first()
        self.assertEqual(reading.register_reading, Decimal('123.45'))
        self.assertEqual(reading.meter_id, "METERID123")




