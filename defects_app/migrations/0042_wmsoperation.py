# Generated manually

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0041_wmscase_wmslot_wmspallettype_wmsstoragecell_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WmsOperation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "operation_type",
                    models.CharField(
                        choices=[
                            ("IMPORT_LOT", "Импорт лота"),
                            ("PLACE", "Размещение"),
                            ("REMOVE", "Снятие с ячейки"),
                            ("MOVE", "Перемещение"),
                            ("REIMPORT_BLOCKED", "Повторный импорт заблокирован"),
                        ],
                        max_length=50,
                        verbose_name="Тип операции",
                    ),
                ),
                ("message", models.TextField(blank=True, verbose_name="Описание")),
                ("data", models.JSONField(blank=True, default=dict, verbose_name="Дополнительные данные")),
                ("performed_by", models.CharField(blank=True, max_length=150, verbose_name="Кто выполнил")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Когда выполнено")),
                (
                    "lot",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="wms_operations",
                        to="defects_app.wmslot",
                        verbose_name="Лот",
                    ),
                ),
                (
                    "container",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="wms_operations",
                        to="defects_app.wmscontainer",
                        verbose_name="Контейнер",
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="wms_operations",
                        to="defects_app.wmscase",
                        verbose_name="Кейс",
                    ),
                ),
                (
                    "pallet",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="operations",
                        to="defects_app.wmspallet",
                        verbose_name="Поддон",
                    ),
                ),
                (
                    "placement",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="operations",
                        to="defects_app.wmspalletplacement",
                        verbose_name="Размещение",
                    ),
                ),
                (
                    "cell",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="wms_operations",
                        to="defects_app.wmsstoragecell",
                        verbose_name="Ячейка",
                    ),
                ),
            ],
            options={
                "verbose_name": "WMS операция",
                "verbose_name_plural": "WMS операции",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]