from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defects_app', '0031_defectphoto_extra_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='avtomobili',
            name='created_on_station_1',
            field=models.BooleanField(default=True, verbose_name='Создана на станции 1'),
        ),
    ]