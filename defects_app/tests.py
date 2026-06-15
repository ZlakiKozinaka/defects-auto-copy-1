from datetime import date
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from openpyxl import Workbook

from defects_app.models import (
    WmsBoxItem,
    WmsContainer,
    WmsLot,
    WmsPallet,
    WmsPalletType,
    WmsSite,
    WmsStorageCell,
    WmsStorageLine,
    WmsStorageUnit,
    WmsWarehouse,
)
from defects_app.services.station1_buffer_service import build_station_one_sequence_number
from defects_app.services.wms_import import import_wms_lot_from_excel
from defects_app.services.wms_storage import can_place_pallet, get_cell_occupancy, place_pallet
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


class WmsStorageServiceTests(TestCase):

    def setUp(self):
        self.site = WmsSite.objects.create(code="test", name="Тестовая площадка")
        self.warehouse = WmsWarehouse.objects.create(site=self.site, name="Основной склад", code="MAIN")
        self.line = WmsStorageLine.objects.create(warehouse=self.warehouse, code="A", name="Ряд A")
        self.cell = WmsStorageCell.objects.create(line=self.line, column_number=1, level_number=1, capacity_units=6)
        self.euro = WmsPalletType.objects.create(name="Евро-поддон", code="EURO", width_units=2)
        self.non_standard = WmsPalletType.objects.create(name="Нестандартный поддон", code="NON_STANDARD", width_units=3)
        self.lot = WmsLot.objects.create(site=self.site, lot_number="D/MY/9-25003-08")
        self.container = WmsContainer.objects.create(lot=self.lot, container_number="FESU5286842")

    def test_can_place_pallet_rejects_overlapping_units(self):
        storage_unit = WmsStorageUnit.objects.create(
            unit_type=WmsStorageUnit.UNIT_CONTAINER,
            container=self.container,
            label=self.container.container_number,
        )
        pallet = WmsPallet.objects.create(pallet_type=self.non_standard, storage_unit=storage_unit)
        place_pallet(pallet, self.cell, 1, 3, AnonymousUser())

        allowed, message = can_place_pallet(self.cell, self.euro, 3, 4)

        self.assertFalse(allowed)
        self.assertIn("пересекается", message)

    def test_cell_occupancy_counts_unique_busy_units(self):
        storage_unit = WmsStorageUnit.objects.create(
            unit_type=WmsStorageUnit.UNIT_CONTAINER,
            container=self.container,
            label=self.container.container_number,
        )
        pallet = WmsPallet.objects.create(pallet_type=self.euro, storage_unit=storage_unit)
        place_pallet(pallet, self.cell, 5, 6, AnonymousUser())

        occupancy = get_cell_occupancy(self.cell)

        self.assertEqual(occupancy["occupied_units"], [5, 6])
        self.assertEqual(occupancy["status"], "partial")


class WmsImportServiceTests(TestCase):

    def setUp(self):
        self.site = WmsSite.objects.create(
            code="test",
            name="Тестовая площадка",
        )

    def build_excel_file(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Case No.", "集装箱编号", "Box No.", "SAP Part Number", "Total QTY", "English Description"])
        sheet.append(["T0210", "FESU5286842", "T0451", "6202500-SZ01-A30J", 6, "Test part"])
        buffer = BytesIO()
        workbook.save(buffer)

        return SimpleUploadedFile(
            "D-MY-9-25003-08.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_wms_lot_creates_hierarchy_from_excel(self):
        result = import_wms_lot_from_excel(
            self.build_excel_file(),
            "D/MY/9-25003-08",
            AnonymousUser(),
            site=self.site,
        )

        self.assertEqual(result.containers_count, 1)
        self.assertEqual(result.cases_count, 1)
        self.assertEqual(result.boxes_count, 1)
        self.assertEqual(result.items_count, 1)

        lot = WmsLot.objects.get()
        self.assertEqual(lot.site, self.site)

        item = WmsBoxItem.objects.get()
        self.assertEqual(item.part_number, "6202500-SZ01-A30J")
        self.assertEqual(item.quantity, Decimal("6"))

    def test_reimport_wms_lot_replaces_previous_hierarchy_without_duplicates(self):
        import_wms_lot_from_excel(
            self.build_excel_file(),
            "D/MY/9-25003-08",
            AnonymousUser(),
            site=self.site,
        )

        result = import_wms_lot_from_excel(
            self.build_excel_file(),
            "D/MY/9-25003-08",
            AnonymousUser(),
            site=self.site,
        )

        self.assertEqual(WmsLot.objects.count(), 1)
        self.assertEqual(WmsContainer.objects.count(), 1)
        self.assertEqual(result.items_count, 1)