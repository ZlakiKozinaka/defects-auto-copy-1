from django.db.models import Q, OuterRef, Subquery

from defects_app.models import Avtomobili, Defekty, StatusAvto


def get_car_by_id(car_id):
    return Avtomobili.objects.filter(id=car_id).select_related("model").first()


def get_car_by_vin(vin):
    return Avtomobili.objects.filter(vin=vin).select_related("model").first()


def get_created_car_by_vin(vin):
    return Avtomobili.objects.filter(
        vin=vin,
        created_on_station_1=True
    ).select_related("model").first()


def get_defects_for_car(car):
    return Defekty.objects.filter(
        avto=car
    ).select_related(
        "tip",
        "oblast",
        "greyd",
        "otvetstvennyj",
        "mesto",
        "smena",
    ).order_by("-data")


def get_last_status_for_car(car):
    return StatusAvto.objects.filter(
        avto=car
    ).order_by("-data_statusa").first()


def get_snp_defects_for_car(car):
    return Defekty.objects.filter(
        avto=car,
        proveren=False,
    ).order_by("-data")


def get_unfixed_defects_for_car(car):
    return Defekty.objects.filter(
        avto=car,
        ustraneno=False,
    ).order_by("-data")


def get_sgp_problem_defects_for_car(car):
    return Defekty.objects.filter(
        avto=car
    ).filter(
        Q(ustraneno=False) | Q(proveren=False)
    ).filter(
        sgp_approval__isnull=True
    ).order_by("-data")


def get_cars_currently_on_snp():
    latest_status = StatusAvto.objects.filter(
        avto=OuterRef("pk")
    ).order_by("-data_statusa")

    return Avtomobili.objects.annotate(
        last_status=Subquery(latest_status.values("status")[:1]),
        last_status_date=Subquery(latest_status.values("data_statusa")[:1]),
    ).filter(
        last_status="СНП"
    ).select_related("model").order_by("last_status_date")

def get_status_history_for_car(car):
    return StatusAvto.objects.filter(
        avto=car
    ).order_by("data_statusa")