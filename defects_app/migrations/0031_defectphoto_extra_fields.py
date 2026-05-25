# Generated manually

from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0030_defectphoto_add_avto"),
    ]

    operations = [
        migrations.AddField(
            model_name="defectphoto",
            name="original_name",
            field=models.CharField(
                max_length=255,
                blank=True,
                null=True,
                verbose_name="Исходное имя файла",
            ),
        ),
        migrations.AddField(
            model_name="defectphoto",
            name="file_size",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Размер файла, байт",
            ),
        ),
        migrations.AddField(
            model_name="defectphoto",
            name="uploaded_by",
            field=models.CharField(
                max_length=150,
                blank=True,
                null=True,
                verbose_name="Кто загрузил",
            ),
        ),

    ]