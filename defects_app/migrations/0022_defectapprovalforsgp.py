from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import now


class Migration(migrations.Migration):

    dependencies = [
        ('defects_app', '0021_dailyproductionplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefectApprovalForSgp',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),

                (
                    'approved_by',
                    models.CharField(
                        max_length=150,
                        verbose_name='Кто согласовал'
                    )
                ),

                (
                    'approved_at',
                    models.DateTimeField(
                        default=now,
                        verbose_name='Дата согласования'
                    )
                ),

                (
                    'comment',
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name='Комментарий согласования'
                    )
                ),

                (
                    'avto',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sgp_defect_approvals',
                        to='defects_app.avtomobili',
                        verbose_name='Автомобиль'
                    )
                ),

                (
                    'defect',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sgp_approval',
                        to='defects_app.defekty',
                        verbose_name='Согласованный дефект'
                    )
                ),
            ],

            options={
                'verbose_name': 'Согласование дефекта для СГП',
                'verbose_name_plural': 'Согласования дефектов для СГП',
                'ordering': ['-approved_at'],
            },
        ),
    ]