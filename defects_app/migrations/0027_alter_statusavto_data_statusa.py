from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0026_alter_vinprefix_comment_alter_vinprefix_is_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="statusavto",
            name="data_statusa",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="Дата статуса"
            ),
        ),
    ]