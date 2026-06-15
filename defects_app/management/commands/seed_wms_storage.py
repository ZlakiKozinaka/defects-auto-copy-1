from django.core.management.base import BaseCommand

from defects_app.models import WmsPalletType, WmsSite, WmsStorageCell, WmsStorageLine, WmsWarehouse


class Command(BaseCommand):
    help = "Создает базовую WMS-конфигурацию склада: A-D, 12 столбцов, 4 этажа и типы поддонов."

    def handle(self, *args, **options):
        site, site_created = WmsSite.objects.get_or_create(
            code="GZHEL",
            defaults={"name": "Гжель", "is_active": True},
        )

        warehouse, warehouse_created = WmsWarehouse.objects.get_or_create(
            site=site,
            code="MAIN",
            defaults={"name": "Основной склад", "is_active": True},
        )

        lines_created = 0
        cells_created = 0
        for sort_order, code in enumerate(["A", "B", "C", "D"], start=1):
            line, created = WmsStorageLine.objects.get_or_create(
                warehouse=warehouse,
                code=code,
                defaults={"name": f"Ряд {code}", "sort_order": sort_order, "is_active": True},
            )
            if created:
                lines_created += 1

            for column_number in range(1, 13):
                for level_number in range(1, 5):
                    _, cell_created = WmsStorageCell.objects.get_or_create(
                        line=line,
                        column_number=column_number,
                        level_number=level_number,
                        defaults={"capacity_units": 6, "is_active": True},
                    )
                    if cell_created:
                        cells_created += 1

        pallet_types = [
            ("EURO", "Евро-поддон", 2),
            ("NON_STANDARD", "Нестандартный поддон", 3),
        ]
        pallet_types_created = 0
        for code, name, width_units in pallet_types:
            _, created = WmsPalletType.objects.update_or_create(
                code=code,
                defaults={"name": name, "width_units": width_units, "is_active": True},
            )
            if created:
                pallet_types_created += 1

        self.stdout.write(self.style.SUCCESS(
            "WMS storage seeded: "
            f"site_created={site_created}, "
            f"warehouse_created={warehouse_created}, "
            f"lines_created={lines_created}, "
            f"cells_created={cells_created}, "
            f"pallet_types_created={pallet_types_created}."
        ))