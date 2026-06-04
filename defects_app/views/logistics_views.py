from urllib.parse import urlencode
from django.urls import reverse
from io import BytesIO

import barcode
from barcode.writer import SVGWriter

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from defects_app.decorators import permission_required, station_session_required
from defects_app.permissions import (
    is_manager_user,
    can_create_cars_and_print,
)
from defects_app.models import Avtomobili, PlanovyeVin, Modeli
from defects_app.forms import CarSearchForm, VIN_PREFIXES
from defects_app.services.station1_buffer_service import (
    add_car_to_station_one_buffer,
    assign_station_one_sequence_number,
    get_station_one_buffer_count,
)
from defects_app.session_utils import require_station_session

def get_created_car_print_url(car_id, batch_car_ids=None):
    url = reverse("print_created_car", kwargs={"car_id": car_id})
    if batch_car_ids:
        url += "?" + urlencode({
            "important_car_ids": ",".join(str(batch_car_id) for batch_car_id in batch_car_ids)
        })
    return url


@permission_required("cars.create_print")
@station_session_required
def create_car_view(request):
    is_manager = is_manager_user(request.user)
    form = CarSearchForm()
    search_form = CarSearchForm()

    car = None
    search_result_car = None
    search_result_plan = None
    search_not_found = False
    show_search_modal = False

    last_created_cars_raw = Avtomobili.objects.order_by("-data_sozdaniya")[:10]

    important_sheet_count = get_station_one_buffer_count()

    last_created_cars = []
    for created_car in last_created_cars_raw:
        plan = PlanovyeVin.objects.filter(vin=created_car.vin).first()
        last_created_cars.append({
            "car": created_car,
            "plan": plan,
        })

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "search_created_car":
            search_form = CarSearchForm(request.POST)
            show_search_modal = True

            if search_form.is_valid():
                vin = search_form.cleaned_data["vin"]

                search_result_car = Avtomobili.objects.filter(vin=vin).first()

                if search_result_car:
                    search_result_plan = PlanovyeVin.objects.filter(vin=search_result_car.vin).first()
                else:
                    search_not_found = True

            return render(request, "defects_app/create_car.html", {
                "form": form,
                "search_form": search_form,
                "car": car,
                "vin_prefixes": VIN_PREFIXES,
                "is_manager": is_manager,
                "last_created_cars": last_created_cars,
                "search_result_car": search_result_car,
                "search_result_plan": search_result_plan,
                "search_not_found": search_not_found,
                "show_search_modal": show_search_modal,
                "important_sheet_count": important_sheet_count,
            })

        form = CarSearchForm(request.POST)

        if form.is_valid():
            vin = form.cleaned_data["vin"]
            model = form.cleaned_data["model"]

            plan_vin = PlanovyeVin.objects.filter(vin=vin).first()

            if not plan_vin:
                messages.error(
                    request,
                    "Такой VIN-номер не был предварительно внесен в базу. Обратитесь к ответственному за формирование VIN-номеров."
                )
                return render(request, "defects_app/create_car.html", {
                    "form": form,
                    "search_form": search_form,
                    "car": None,
                    "vin_prefixes": VIN_PREFIXES,
                    "is_manager": is_manager,
                    "last_created_cars": last_created_cars,
                    "search_result_car": search_result_car,
                    "search_result_plan": search_result_plan,
                    "search_not_found": search_not_found,
                    "show_search_modal": show_search_modal,
                    "important_sheet_count": important_sheet_count,
                })

            existing_car = Avtomobili.objects.filter(vin=vin).first()

            if existing_car:
                if not existing_car.created_on_station_1:
                    existing_car.created_on_station_1 = True
                    existing_car.kto_sozdal = request.user.username
                    existing_car.data_sozdaniya = timezone.now()
                    existing_car.save(update_fields=[
                        "created_on_station_1",
                        "kto_sozdal",
                        "data_sozdaniya",
                    ])
                    assign_station_one_sequence_number(existing_car)
                    batch_car_ids = add_car_to_station_one_buffer(existing_car)

                    messages.success(request, "Машина успешно создана на станции 1.")
                    return redirect(get_created_car_print_url(existing_car.id, batch_car_ids))

                messages.info(request, "Машина с таким VIN уже существует.")
                return redirect(f"/create-car/?car_id={existing_car.id}")

            model_name = plan_vin.model.strip()

            model_obj, created = Modeli.objects.get_or_create(
                nazvanie=model_name
            )

            car = Avtomobili.objects.create(
                vin=vin,
                model=model_obj,
                kto_sozdal=request.user.username,
                data_sozdaniya=timezone.now(),
            )
            assign_station_one_sequence_number(car)
            batch_car_ids = add_car_to_station_one_buffer(car)

            messages.success(request, "Новая машина успешно создана.")
            return redirect(get_created_car_print_url(car.id, batch_car_ids))

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

    return render(request, "defects_app/create_car.html", {
        "form": form,
        "search_form": search_form,
        "car": car,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager,
        "last_created_cars": last_created_cars,
        "search_result_car": search_result_car,
        "search_result_plan": search_result_plan,
        "search_not_found": search_not_found,
        "show_search_modal": show_search_modal,
        "important_sheet_count": important_sheet_count,
    })

@login_required
def print_created_car_view(request, car_id):
    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response
    if not can_create_cars_and_print(request.user):
        return HttpResponseForbidden("У вас нет прав на печать карточек автомобиля.")

    car = get_object_or_404(Avtomobili, id=car_id)

    plan_vin = PlanovyeVin.objects.filter(vin=car.vin).first()
    vin_barcode_svg = generate_vin_barcode_svg(car.vin)
    kolichestvo_mest = "7" if "C2A7" in car.vin or (plan_vin and "/7_" in plan_vin.komplektaciya) else "5"

    stations = [ ]
    #     "1. Бестеневая",
    #     "2. OkLine",
    #     "3. Телематика",
    #     "4. Глонасс",
    #     "5. Батарея",
    #     "6. Передний двигатель",
    #     "7. Задний двигатель",
    #     "8. Станция 3 – Качество",
    #     "9. T20 – Качество",
    #     "10. C06 – Качество",
    #     "11. Доводка",
    # ]

    aggregates = [
        "Телематика",
        "Глонасс",
        "Батарея",
        "Передний двигатель",
        "Задний двигатель",
    ]

    important_print_url = None
    important_car_ids_raw = request.GET.get("important_car_ids", "")
    important_car_ids = [
        car_id.strip()
        for car_id in important_car_ids_raw.split(",")
        if car_id.strip().isdigit()
    ][:6]
    if important_car_ids:
        important_print_url = reverse("print_created_car_info_batch") + "?" + urlencode({
            "car_ids": ",".join(important_car_ids)
        })

    return render(request, "defects_app/print_created_car.html", {
        "car": car,
        "stations": stations,
        "aggregates": aggregates,
        "plan_vin": plan_vin,
        "vin_barcode_svg": vin_barcode_svg,
        "kolichestvo_mest": kolichestvo_mest,
        "important_print_url": important_print_url,
    })

@login_required
def print_created_car_info_view(request, car_id):
    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response
    if not can_create_cars_and_print(request.user):
        return HttpResponseForbidden("У вас нет прав на печать карточек автомобиля.")

    car = get_object_or_404(Avtomobili, id=car_id)
    plan_vin = PlanovyeVin.objects.filter(vin=car.vin).first()
    vin_barcode_svg = generate_vin_barcode_svg(car.vin)
    kolichestvo_mest = "7" if "C2A7" in car.vin or (plan_vin and "/7_" in plan_vin.komplektaciya) else "5"

    return render(request, "defects_app/print_created_car_info.html", {
        "car": car,
        "plan_vin": plan_vin,
        "vin_barcode_svg": vin_barcode_svg,
        "kolichestvo_mest": kolichestvo_mest,
    })


@login_required
def print_created_car_info_batch_view(request):
    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response
    if not can_create_cars_and_print(request.user):
        return HttpResponseForbidden("У вас нет прав на печать карточек автомобиля.")

    car_ids_raw = request.GET.get("car_ids", "")
    car_ids = [int(car_id.strip()) for car_id in car_ids_raw.split(",") if car_id.strip().isdigit()][:6]

    if not car_ids:
        return HttpResponseBadRequest("Не переданы данные для печати важного листа.")

    cars = Avtomobili.objects.filter(id__in=car_ids)
    cars_by_id = {car.id: car for car in cars}

    print_rows = []
    for car_id in car_ids:
        car = cars_by_id.get(car_id)
        if not car:
            continue
        plan_vin = PlanovyeVin.objects.filter(vin=car.vin).first()
        kolichestvo_mest = "7" if "C2A7" in car.vin or (plan_vin and "/7_" in plan_vin.komplektaciya) else "5"
        print_rows.append({
            "car": car,
            "plan_vin": plan_vin,
            "vin_barcode_svg": generate_vin_barcode_svg(car.vin),
            "kolichestvo_mest": kolichestvo_mest,
        })

    if not print_rows:
        return HttpResponseBadRequest("Не удалось подготовить данные для печати важного листа.")

    return render(request, "defects_app/print_created_car_info_batch.html", {
        "print_rows": print_rows,
    })

def generate_vin_barcode_svg(vin):
    code128 = barcode.get("code128", vin, writer=SVGWriter())
    buffer = BytesIO()
    code128.write(buffer, options={
        "write_text": True,
        "module_height": 18,
        "font_size": 10,
        "quiet_zone": 2,
    })
    return buffer.getvalue().decode("utf-8")