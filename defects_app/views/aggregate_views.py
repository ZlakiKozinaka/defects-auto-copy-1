from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from defects_app.session_utils import require_station_session

from defects_app.decorators import permission_required, station_session_required
from defects_app.permissions import (
    is_manager_user,
    can_fix_aggregates,
    can_edit_aggregates,
)
from defects_app.models import Avtomobili
from defects_app.forms import (
    CarSearchForm,
    TelematikaForm,
    GlonassForm,
    BatareyaForm,
    PerednijDvigatelForm,
    ZadnijDvigatelForm,
    VIN_PREFIXES,
)

from defects_app.services.aggregate_service import (
    bind_telematika,
    bind_glonass,
    bind_car_component,
)

@login_required
def telematika_view(request):
    is_manager = is_manager_user(request.user)

    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response

    station_id = session_data["station_id"]

    if not can_fix_aggregates(request.user):
        return HttpResponseForbidden("Для вашей станции эта форма недоступна.")

    form = CarSearchForm()
    telematika_form = TelematikaForm()
    car = None
    locked = False

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        if car.telematika:
            telematika_form = TelematikaForm(initial={
                "telematika": car.telematika
            })

            if not is_manager:
                locked = True

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)
            telematika_form = TelematikaForm()

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = Avtomobili.objects.filter(
                    vin=vin,
                    created_on_station_1=True
                ).first()

                if car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/telematika/?car_id={car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")

        elif action == "bind":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            if car.telematika and not is_manager:
                messages.error(request, "Телематика уже привязана. Изменение доступно только начальнику.")
                return redirect(f"/telematika/?car_id={car.id}")

            form = CarSearchForm(initial={
                "vin": car.vin,
                "model": car.model
            })
            telematika_form = TelematikaForm(request.POST)

            if telematika_form.is_valid():
                new_telematika = telematika_form.cleaned_data["telematika"]

                old_telematika = bind_telematika(
                    car=car,
                    user=request.user,
                    new_telematika=new_telematika,
                )

                if old_telematika and is_manager:
                    messages.success(request, "Телематика успешно изменена.")
                else:
                    messages.success(request, "Телематика успешно привязана.")

                return redirect(f"/telematika/?car_id={car.id}")

    return render(request, "defects_app/telematika.html", {
        "form": form,
        "telematika_form": telematika_form,
        "car": car,
        "vin_prefixes": VIN_PREFIXES,
        "locked": locked,
        "is_manager": is_manager,
    })



@login_required
def glonass_view(request):
    is_manager = is_manager_user(request.user)
    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response

    station_id = session_data["station_id"]
    if not can_fix_aggregates(request.user):
        return HttpResponseForbidden("Для вашей станции эта форма недоступна.")

    

    form = CarSearchForm()
    glonass_form = GlonassForm()
    car = None
    locked = False

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        if car.glonass:
            glonass_form = GlonassForm(initial={
                "glonass": car.glonass
            })

            if not is_manager:
                locked = True

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)
            glonass_form = GlonassForm()

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = Avtomobili.objects.filter(
                    vin=vin,
                    created_on_station_1=True
                ).first()

                if car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/glonass/?car_id={car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")

        elif action == "bind":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            if car.glonass and not can_edit_aggregates(request.user):
                messages.error(request, "ГЛОНАСС уже привязан. Изменение доступно только начальнику.")
                return redirect(f"/glonass/?car_id={car.id}")

            form = CarSearchForm(initial={
                "vin": car.vin,
                "model": car.model
            })
            glonass_form = GlonassForm(request.POST)

            old_glonass = car.glonass
            old_sn = car.glonass_sn
            old_imei = car.glonass_imei
            old_iccid = car.glonass_iccid

            if glonass_form.is_valid():
                glonass_text = glonass_form.cleaned_data["glonass"]
                sn, imei, iccid = parse_glonass_data(glonass_text)

                save_avto_history(car, "glonass", old_glonass, glonass_text, request.user.username)
                save_avto_history(car, "glonass_sn", old_sn, sn, request.user.username)
                save_avto_history(car, "glonass_imei", old_imei, imei, request.user.username)
                save_avto_history(car, "glonass_iccid", old_iccid, iccid, request.user.username)

                car.glonass = glonass_text
                car.glonass_sn = sn
                car.glonass_imei = imei
                car.glonass_iccid = iccid

                if not old_glonass:
                    car.glonass_kto = request.user.username
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

                if old_glonass and is_manager:
                    messages.success(request, "Глонасс успешно изменен.")
                else:
                    messages.success(request, "Глонасс успешно привязан.")

                return redirect(f"/glonass/?car_id={car.id}")

    return render(request, "defects_app/glonass.html", {
        "form": form,
        "glonass_form": glonass_form,
        "car": car,
        "vin_prefixes": VIN_PREFIXES,
        "locked": locked,
        "is_manager": is_manager,
    })


# glonas i batareia vmeste

@permission_required("aggregates.fix")
@station_session_required
def telematika_glonass_view(request):
    is_manager = is_manager_user(request.user)
    station_id = request.station_context["station_id"]

    form = CarSearchForm()
    telematika_form = TelematikaForm()
    glonass_form = GlonassForm()

    car = None
    telematika_locked = False
    glonass_locked = False

    car_id = request.GET.get("car_id")

    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)

        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        if car.telematika:
            telematika_form = TelematikaForm(initial={
                "telematika": car.telematika
            })
            if not can_edit_aggregates(request.user):
                telematika_locked = True

        if car.glonass:
            glonass_form = GlonassForm(initial={
                "glonass": car.glonass
            })
            if not can_edit_aggregates(request.user):
                glonass_locked = True

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = Avtomobili.objects.filter(
                    vin=vin,
                    created_on_station_1=True
                ).first()

                if car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/telematika-glonass/?car_id={car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")

        elif action == "save_telematika":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            if car.telematika and not is_manager:
                messages.error(request, "Телематика уже привязана. Изменение доступно только начальнику.")
                return redirect(f"/telematika-glonass/?car_id={car.id}")

            telematika_form = TelematikaForm(request.POST)

            if telematika_form.is_valid():
                new_telematika = telematika_form.cleaned_data["telematika"]

                old_telematika = bind_telematika(
                    car=car,
                    user=request.user,
                    new_telematika=new_telematika,
                )

                if not old_telematika:
                    messages.success(request, "Телематика успешно привязана.")
                else:
                    messages.success(request, "Телематика успешно изменена.")

                return redirect(f"/telematika-glonass/?car_id={car.id}")

        elif action == "save_glonass":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            if car.glonass and not is_manager:
                messages.error(request, "ГЛОНАСС уже привязан. Изменение доступно только начальнику.")
                return redirect(f"/telematika-glonass/?car_id={car.id}")

            glonass_form = GlonassForm(request.POST)

            if glonass_form.is_valid():
                glonass_text = glonass_form.cleaned_data["glonass"]

                old_glonass = bind_glonass(
                    car=car,
                    user=request.user,
                    glonass_text=glonass_text,
                )

                if not old_glonass:
                    messages.success(request, "ГЛОНАСС успешно привязан.")
                else:
                    messages.success(request, "ГЛОНАСС успешно изменен.")

                return redirect(f"/telematika-glonass/?car_id={car.id}")

    return render(request, "defects_app/telematika_glonass.html", {
        "form": form,
        "telematika_form": telematika_form,
        "glonass_form": glonass_form,
        "car": car,
        "vin_prefixes": VIN_PREFIXES,
        "telematika_locked": telematika_locked,
        "glonass_locked": glonass_locked,
        "is_manager": is_manager,
    })



@login_required
def batareya_view(request):
    return redirect("/agregaty/")


@login_required
def perednij_dvigatel_view(request):
    return redirect("/agregaty/")


@login_required
def zadnij_dvigatel_view(request):
    return redirect("/agregaty/")

@permission_required("aggregates.fix")
@station_session_required
def agregaty_view(request):
    is_manager = is_manager_user(request.user)
    station_id = request.station_context["station_id"]

    form = CarSearchForm()
    car = None

    batareya_form = BatareyaForm()
    perednij_form = PerednijDvigatelForm()
    zadnij_form = ZadnijDvigatelForm()

    car_id = request.GET.get("car_id")

    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)

        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        batareya_form = BatareyaForm(initial={
            "batareya": car.batareya
        })

        perednij_form = PerednijDvigatelForm(initial={
            "perednij_dvigatel": car.perednij_dvigatel
        })

        zadnij_form = ZadnijDvigatelForm(initial={
            "zadnij_dvigatel": car.zadnij_dvigatel
        })

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = Avtomobili.objects.filter(
                    vin=vin,
                    created_on_station_1=True
                ).first()

                if car:
                    return redirect(f"/agregaty/?car_id={car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")

        elif action == "bind":
            car_id_post = request.POST.get("car_id")
            component = request.POST.get("component")

            car = get_object_or_404(Avtomobili, id=car_id_post)

            if component == "batareya":
                if car.batareya and not can_edit_aggregates(request.user):
                    messages.error(request, "Батарея уже привязана. Изменение доступно только начальнику.")
                    return redirect(f"/agregaty/?car_id={car.id}")

                batareya_form = BatareyaForm(request.POST)

                if batareya_form.is_valid():
                    new_value = batareya_form.cleaned_data["batareya"]

                    bind_car_component(
                        car=car,
                        user=request.user,
                        field_name="batareya",
                        new_value=new_value,
                        user_field="batareya_kto",
                        date_field="batareya_kogda",
                    )

                    messages.success(request, "Батарея сохранена.")
                    return redirect(f"/agregaty/?car_id={car.id}")

            elif component == "perednij_dvigatel":
                if car.perednij_dvigatel and not can_edit_aggregates(request.user):
                    messages.error(request, "Передний двигатель уже привязан. Изменение доступно только начальнику.")
                    return redirect(f"/agregaty/?car_id={car.id}")

                perednij_form = PerednijDvigatelForm(request.POST)

                if perednij_form.is_valid():
                    new_value = perednij_form.cleaned_data["perednij_dvigatel"]

                    bind_car_component(
                        car=car,
                        user=request.user,
                        field_name="perednij_dvigatel",
                        new_value=new_value,
                        user_field="perednij_dvigatel_kto",
                        date_field="perednij_dvigatel_kogda",
                    )

                    messages.success(request, "Передний двигатель сохранён.")
                    return redirect(f"/agregaty/?car_id={car.id}")

            elif component == "zadnij_dvigatel":
                if car.zadnij_dvigatel and not can_edit_aggregates(request.user):
                    messages.error(request, "Задний двигатель уже привязан. Изменение доступно только начальнику.")
                    return redirect(f"/agregaty/?car_id={car.id}")

                zadnij_form = ZadnijDvigatelForm(request.POST)

                if zadnij_form.is_valid():
                    new_value = zadnij_form.cleaned_data["zadnij_dvigatel"]

                    bind_car_component(
                        car=car,
                        user=request.user,
                        field_name="zadnij_dvigatel",
                        new_value=new_value,
                        user_field="zadnij_dvigatel_kto",
                        date_field="zadnij_dvigatel_kogda",
                    )

                    messages.success(request, "Задний двигатель сохранён.")
                    return redirect(f"/agregaty/?car_id={car.id}")

    return render(request, "defects_app/agregaty.html", {
        "form": form,
        "car": car,
        "batareya_form": batareya_form,
        "perednij_form": perednij_form,
        "zadnij_form": zadnij_form,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager,
    })
