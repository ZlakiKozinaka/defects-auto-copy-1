from datetime import date

from django.test import SimpleTestCase

from defects_app.services.station1_buffer_service import build_station_one_sequence_number
from defects_app.views.logistics_views import get_created_car_print_url


class StationOneSequenceNumberTests(SimpleTestCase):
    def test_build_station_one_sequence_number_uses_day_month_year_and_three_digits(self):
        sequence_number = build_station_one_sequence_number(date(2026, 6, 2), 1)

        self.assertEqual(sequence_number, "02062026001")

    def test_build_station_one_sequence_number_increments_within_same_day(self):
        sequence_number = build_station_one_sequence_number(date(2026, 6, 2), 23)

        self.assertEqual(sequence_number, "02062026023")

    def test_build_station_one_sequence_number_restarts_when_date_changes(self):
        sequence_number = build_station_one_sequence_number(date(2026, 6, 3), 1)

        self.assertEqual(sequence_number, "03062026001")


class CreatedCarPrintUrlTests(SimpleTestCase):
    def test_get_created_car_print_url_without_batch(self):
        self.assertEqual(get_created_car_print_url(10), "/print-created-car/10/")

    def test_get_created_car_print_url_with_batch(self):
        self.assertEqual(
            get_created_car_print_url(10, [1, 2, 3, 4, 5, 6]),
            "/print-created-car/10/?important_car_ids=1%2C2%2C3%2C4%2C5%2C6",
        )