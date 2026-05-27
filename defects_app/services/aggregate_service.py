import re

from django.utils import timezone

from defects_app.services.history_service import save_avto_history


def parse_glonass_data(glonass_text):
    if not glonass_text:
        return None, None, None

    text = glonass_text.strip()

    sn_match = re.search(r"SN\s*:\s*([^;]+)", text, re.IGNORECASE)
    imei_match = re.search(r"IMEI\s*:\s*([^;]+)", text, re.IGNORECASE)
    iccid_match = re.search(r"ICCID\s*:\s*([^;]+)", text, re.IGNORECASE)

    sn = sn_match.group(1).strip() if sn_match else None
    imei = imei_match.group(1).strip() if imei_match else None
    iccid = iccid_match.group(1).strip() if iccid_match else None

    return sn, imei, iccid


def bind_telematika(car, user, new_telematika):
    old_telematika = car.telematika

    save_avto_history(
        car,
        "telematika",
        old_telematika,
        new_telematika,
        user.username
    )

    car.telematika = new_telematika

    if not old_telematika:
        car.privyazal_telematiku = user.username
        car.data_privyazki_telematiki = timezone.now()
        car.save(update_fields=[
            "telematika",
            "privyazal_telematiku",
            "data_privyazki_telematiki",
        ])
    else:
        car.save(update_fields=["telematika"])

    return old_telematika


def bind_glonass(car, user, glonass_text):
    old_glonass = car.glonass
    old_sn = car.glonass_sn
    old_imei = car.glonass_imei
    old_iccid = car.glonass_iccid

    sn, imei, iccid = parse_glonass_data(glonass_text)

    save_avto_history(car, "glonass", old_glonass, glonass_text, user.username)
    save_avto_history(car, "glonass_sn", old_sn, sn, user.username)
    save_avto_history(car, "glonass_imei", old_imei, imei, user.username)
    save_avto_history(car, "glonass_iccid", old_iccid, iccid, user.username)

    car.glonass = glonass_text
    car.glonass_sn = sn
    car.glonass_imei = imei
    car.glonass_iccid = iccid

    if not old_glonass:
        car.glonass_kto = user.username
        car.glonass_kogda = timezone.now()
        car.save(update_fields=[
            "glonass",
            "glonass_sn",
            "glonass_imei",
            "glonass_iccid",
            "glonass_kto",
            "glonass_kogda",
        ])
    else:
        car.save(update_fields=[
            "glonass",
            "glonass_sn",
            "glonass_imei",
            "glonass_iccid",
        ])

    return old_glonass


def bind_car_component(car, user, field_name, new_value, user_field, date_field):
    old_value = getattr(car, field_name)

    save_avto_history(
        car,
        field_name,
        old_value,
        new_value,
        user.username
    )

    setattr(car, field_name, new_value)

    if not old_value:
        setattr(car, user_field, user.username)
        setattr(car, date_field, timezone.now())
        car.save(update_fields=[
            field_name,
            user_field,
            date_field,
        ])
    else:
        car.save(update_fields=[field_name])

    return old_value