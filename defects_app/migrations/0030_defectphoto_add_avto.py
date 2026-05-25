from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0029_defectphoto"),
    ]

    operations = [
        migrations.AddField(
            model_name="defectphoto",
            name="avto",
            field=models.ForeignKey(
                to="defects_app.avtomobili",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="defect_photos",
                verbose_name="Автомобиль",
                null=True,
                blank=True,
            ),
        ),
    ]