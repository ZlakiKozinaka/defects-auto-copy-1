from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0020_planovyevin"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyProductionPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(unique=True, verbose_name="Дата")),
                ("plan_count", models.PositiveIntegerField(verbose_name="План машин за смену")),
                ("created_by", models.CharField(blank=True, max_length=150, null=True, verbose_name="Кто создал")),
                ("updated_by", models.CharField(blank=True, max_length=150, null=True, verbose_name="Кто изменил")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата изменения")),
            ],
            options={
                "verbose_name": "План выпуска",
                "verbose_name_plural": "Планы выпуска",
                "ordering": ["-date"],
            },
        ),
    ]