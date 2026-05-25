from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0028_alter_avtomobili_data_sozdaniya"),
    ]

    operations = [
        migrations.CreateModel(
            name="DefectPhoto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),

                (
                    "image",
                    models.ImageField(
                        upload_to="defects_photos/%Y/%m/%d/",
                        verbose_name="Фото",
                    ),
                ),

                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Дата загрузки",
                    ),
                ),

                (
                    "defect",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="defects_app.defekty",
                        verbose_name="Дефект",
                    ),
                ),
            ],

            options={
                "verbose_name": "Фото дефекта",
                "verbose_name_plural": "Фото дефектов",
                "ordering": ["-uploaded_at"],
            },
        ),
    ]