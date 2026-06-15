from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0043_wmsboxitem_row_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="wmscontainer",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активен"),
        ),
        migrations.AddField(
            model_name="wmscase",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активен"),
        ),
        migrations.AddField(
            model_name="wmsbox",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активен"),
        ),
        migrations.AddField(
            model_name="wmsboxitem",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активна"),
        ),
        migrations.AlterField(
            model_name="wmsoperation",
            name="operation_type",
            field=models.CharField(
                choices=[
                    ("IMPORT_LOT", "Импорт лота"),
                    ("PLACE", "Размещение"),
                    ("REMOVE", "Снятие с ячейки"),
                    ("MOVE", "Перемещение"),
                    ("REIMPORT_BLOCKED", "Повторный импорт заблокирован"),
                    ("PICK", "Выдача детали"),
                    ("CLOSE_ITEM", "Закрытие позиции"),
                    ("CLOSE_BOX", "Закрытие коробки"),
                    ("CLOSE_CASE", "Закрытие кейса"),
                    ("CLOSE_CONTAINER", "Закрытие контейнера"),
                    ("CLOSE_LOT", "Закрытие лота"),
                ],
                max_length=50,
                verbose_name="Тип операции",
            ),
        ),
    ]