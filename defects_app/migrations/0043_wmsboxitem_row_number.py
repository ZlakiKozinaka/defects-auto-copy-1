# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0042_wmsoperation"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="wmsboxitem",
            name="unique_wms_item_part_per_box",
        ),
        migrations.AddField(
            model_name="wmsboxitem",
            name="row_number",
            field=models.PositiveIntegerField(default=0, verbose_name="Номер строки Excel"),
        ),
        migrations.AddConstraint(
            model_name="wmsboxitem",
            constraint=models.UniqueConstraint(
                fields=("box", "part_number", "row_number"),
                name="unique_wms_item_part_row_per_box",
            ),
        ),
    ]