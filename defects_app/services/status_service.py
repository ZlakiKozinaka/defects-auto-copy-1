# defects_app/services/status_service.py

from django.utils import timezone

from defects_app.models import StatusAvto, Defekty, SnpDefectComment, DefectApprovalForSgp


STATUS_SNP = "СНП"
STATUS_SGP = "СГП"


def get_last_car_status(car):
    return StatusAvto.objects.filter(
        avto=car
    ).order_by("-data_statusa").first()


def car_is_on_sgp(car):
    last_status = get_last_car_status(car)
    return bool(last_status and last_status.status == STATUS_SGP)


def car_is_on_snp(car):
    last_status = get_last_car_status(car)
    return bool(last_status and last_status.status == STATUS_SNP)


def car_passed_bestenevaya(car):
    return bool(car.proshla_bestenevaya and car.data_prohoda_bestenevaya)


def send_car_to_snp(car, user):
    if car_is_on_sgp(car):
        raise ValueError("Машина уже находится в СГП. На СНП её отправить нельзя.")

    StatusAvto.objects.create(
        avto=car,
        status=STATUS_SNP,
        kto_izmenil=user.username,
    )


def send_car_to_sgp(car, user):
    if car_is_on_sgp(car):
        raise ValueError("Машина уже находится в СГП.")

    StatusAvto.objects.create(
        avto=car,
        status=STATUS_SGP,
        kto_izmenil=user.username,
    )


def get_sgp_problem_defects(car):
    return Defekty.objects.filter(
        avto=car
    ).filter(
        ustraneno=False
    ) | Defekty.objects.filter(
        avto=car,
        proveren=False
    )


def approve_defects_for_sgp(car, user, comment=""):
    problem_defects = Defekty.objects.filter(
        avto=car
    ).filter(
        ustraneno=False
    ) | Defekty.objects.filter(
        avto=car,
        proveren=False
    )

    problem_defects = problem_defects.filter(
        sgp_approval__isnull=True
    ).distinct()

    for defect in problem_defects:
        DefectApprovalForSgp.objects.create(
            defect=defect,
            avto=car,
            approved_by=user.username,
            comment=comment,
        )

    return problem_defects.count()


def add_snp_comment(defect, car, user, comment_text):
    SnpDefectComment.objects.create(
        defect=defect,
        avto=car,
        comment=comment_text,
        kto_sozdal=user.username,
    )


def mark_defect_fixed(defect, user):
    defect.ustraneno = True
    defect.kto_ustranil = user.username
    defect.data_ustraneniya = timezone.now()
    defect.save(update_fields=[
        "ustraneno",
        "kto_ustranil",
        "data_ustraneniya",
    ])


def mark_defect_verified(defect, user):
    defect.proveren = True
    defect.kto_razreshil = user.username
    defect.data_razresheniya = timezone.now()
    defect.save(update_fields=[
        "proveren",
        "kto_razreshil",
        "data_razresheniya",
    ])