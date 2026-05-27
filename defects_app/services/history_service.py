# defects_app/services/history_service.py

from defects_app.models import (
    IstoriyaIzmeneniyAvto,
    IstoriyaIzmeneniyDefektov,
)


def save_avto_history(avto, field_name, old_value, new_value, username):
    old_str = "" if old_value is None else str(old_value)
    new_str = "" if new_value is None else str(new_value)

    if old_str and old_str != new_str:
        IstoriyaIzmeneniyAvto.objects.create(
            avto=avto,
            pole=field_name,
            staroe_znachenie=old_str,
            novoe_znachenie=new_str,
            kto_izmenil=username,
        )


def save_defect_history(defect, field_name, old_value, new_value, username):
    old_str = "" if old_value is None else str(old_value)
    new_str = "" if new_value is None else str(new_value)

    if old_str != new_str:
        IstoriyaIzmeneniyDefektov.objects.create(
            defekt=defect,
            pole=field_name,
            staroe_znachenie=old_str,
            novoe_znachenie=new_str,
            kto_izmenil=username,
        )