# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0027_alter_statusavto_data_statusa"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avtomobili",
            name="data_sozdaniya",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="Дата создания",
            ),
        ),
    ]