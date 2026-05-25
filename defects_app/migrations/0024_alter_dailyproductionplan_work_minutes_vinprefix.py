# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0023_dailyproductionplan_work_minutes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailyproductionplan",
            name="work_minutes",
            field=models.PositiveIntegerField(
                default=450,
                verbose_name="Рабочие минуты"
            ),
        ),

        migrations.CreateModel(
            name="VinPrefix",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID"
                    ),
                ),
                (
                    "prefix",
                    models.CharField(
                        max_length=17,
                        unique=True,
                        verbose_name="Префикс VIN"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        verbose_name="Показывать в выпадающем списке"
                    ),
                ),
                (
                    "comment",
                    models.CharField(
                        max_length=255,
                        blank=True,
                        null=True,
                        verbose_name="Комментарий"
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vin_prefixes",
                        to="defects_app.modeli",
                        verbose_name="Модель"
                    ),
                ),
            ],
            options={
                "verbose_name": "Префикс VIN",
                "verbose_name_plural": "Префиксы VIN",
                "ordering": ["model__nazvanie", "prefix"],
            },
        ),
    ]