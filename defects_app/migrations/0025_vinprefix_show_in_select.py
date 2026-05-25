# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0024_alter_dailyproductionplan_work_minutes_vinprefix"),
    ]

    operations = [
        migrations.AddField(
            model_name="vinprefix",
            name="show_in_select",
            field=models.BooleanField(default=True, verbose_name="Показывать в списке выбора модели"),
        ),
    ]