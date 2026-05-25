# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0025_vinprefix_show_in_select"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vinprefix",
            name="comment",
            field=models.CharField(
                max_length=150,
                blank=True,
                null=True,
                verbose_name="Комментарий"
            ),
        ),
        migrations.AlterField(
            model_name="vinprefix",
            name="is_active",
            field=models.BooleanField(
                default=True,
                verbose_name="Активен для автоподстановки"
            ),
        ),
        migrations.AlterField(
            model_name="vinprefix",
            name="prefix",
            field=models.CharField(
                max_length=17,
                verbose_name="Начало VIN"
            ),
        ),
        migrations.AlterField(
            model_name="vinprefix",
            name="show_in_select",
            field=models.BooleanField(
                default=True,
                verbose_name="Показывать в списке"
            ),
        ),
    ]