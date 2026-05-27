from django.contrib.auth import logout

from defects_app.models import Mesta, Smeny
from defects_app.services.history_service import save_defect_history
from defects_app.services.photo_service import save_defect_photos


def create_defect_for_car(car, form, request, station_id, shift_id):
    defect = form.save(commit=False)

    defect.avto = car
    defect.kto_sozdal = request.user.username

    auto_mesto = Mesta.objects.filter(id=station_id).first()
    auto_smena = Smeny.objects.filter(id=shift_id).first()

    if not auto_mesto or not auto_smena:
        logout(request)
        return None, "LOGIN_REQUIRED"

    defect.mesto = auto_mesto
    defect.smena = auto_smena
    defect.save()

    save_defect_photos(defect, request)

    return defect, None

def update_defect_from_form(defect, form, request):
    original_defect = defect.__class__.objects.get(id=defect.id)

    updated_defect = form.save(commit=False)

    updated_defect.avto = original_defect.avto
    updated_defect.kto_sozdal = original_defect.kto_sozdal
    updated_defect.data = original_defect.data
    updated_defect.mesto = original_defect.mesto
    updated_defect.smena = original_defect.smena

    updated_defect.save()

    save_defect_photos(updated_defect, request)

    fields_for_history = [
        "smena",
        "mesto",
        "tip",
        "oblast",
        "greyd",
        "otvetstvennyj",
        "stanciya",
        "kommentarij",
    ]

    for field_name in fields_for_history:
        save_defect_history(
            updated_defect,
            field_name,
            getattr(original_defect, field_name),
            getattr(updated_defect, field_name),
            request.user.username,
        )

    return updated_defect

