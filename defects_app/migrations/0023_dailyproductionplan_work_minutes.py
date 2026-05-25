from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defects_app", "0022_defectapprovalforsgp"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailyproductionplan",
            name="work_minutes",
            field=models.PositiveIntegerField(default=450),
        ),
    ]