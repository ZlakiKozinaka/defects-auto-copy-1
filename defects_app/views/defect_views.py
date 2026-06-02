from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from defects_app.models import SnpDefectOrder
from defects_app.session_utils import require_station_session

from defects_app.decorators import permission_required, station_session_required
from defects_app.permissions import (
    has_permission,
    is_manager_user,
    can_edit_delete_defects,
    can_create_cars_and_print,
)
from defects_app.models import (
    Avtomobili,
    Defekty,
    StatusAvto,
    PlanovyeVin,
    Modeli,
    ContainerCar,
    ContainerReceipt,
)

from defects_app.selectors import (
    get_car_by_vin,
    get_created_car_by_vin,
    get_defects_for_car,
    get_last_status_for_car,
    get_snp_defects_for_car,
    get_unfixed_defects_for_car,
    get_sgp_problem_defects_for_car,
    get_status_history_for_car,
    get_latest_container_receipts,
)

from defects_app.forms import (
    CarSearchForm,
    DefectForm,
    VIN_PREFIXES,
)

from defects_app.services.defect_service import (
    create_defect_for_car,
    update_defect_from_form,
)

from defects_app.services.photo_service import save_defect_photos
from defects_app.services.history_service import save_defect_history
from defects_app.services.status_service import (
    car_passed_bestenevaya,
    send_car_to_snp,
    send_car_to_sgp,
    approve_defects_for_sgp,
    add_snp_comment,
    mark_defect_fixed,
    mark_defect_verified,
)
from defects_app.views_helpers import is_vh1_station


@permission_required("defects.create")
@station_session_required
def home(request):
    station_id = request.station_context["station_id"]
    is_manager = can_edit_delete_defects(request.user)

    form = CarSearchForm()
    car = None
    defects = []

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })
        defects = get_defects_for_car(car)

    if request.method == "POST":
        action = request.POST.get("action")        

        if action == "save" and not can_create_cars_and_print(request.user):
            messages.error(request, "Создание машины доступно только логистике и начальникам.")
            return render(request, "defects_app/home.html", {
                "form": form,
                "car": car,
                "defects": defects,
                "vin_prefixes": VIN_PREFIXES,
                "is_manager": is_manager,
            })

        current_car_id = request.POST.get("current_car_id")
        if current_car_id and action in ["find", "save"]:
            current_car = get_object_or_404(Avtomobili, id=current_car_id)

            if not current_car.proshla_bestenevaya:
                messages.error(
                    request,
                    "Сначала завершите текущую машину: нажмите «Машина прошла станцию Бестеневая»."
                )

                defects = get_defects_for_car(current_car)
                form = CarSearchForm(initial={
                    "vin": current_car.vin,
                    "model": current_car.model
                })

                return render(request, "defects_app/home.html", {
                    "form": form,
                    "car": current_car,
                    "defects": defects,
                    "vin_prefixes": VIN_PREFIXES,
                    "is_manager": is_manager,
                })

        form = CarSearchForm(request.POST)

        if form.is_valid():
            vin = form.cleaned_data["vin"]
            model = form.cleaned_data["model"]

            existing_car = get_car_by_vin(vin)

            if action == "find":
                if existing_car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/?car_id={existing_car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")
                    return render(request, "defects_app/home.html", {
                        "form": form,
                        "car": None,
                        "defects": [],
                        "vin_prefixes": VIN_PREFIXES,
                        "is_manager": is_manager,
                    })

            elif action == "save":
                if existing_car:
                    messages.info(request, "Машина с таким VIN уже существует. Открыта существующая запись.")
                    return redirect(f"/?car_id={existing_car.id}")
                else:
                    car = Avtomobili.objects.create(
                        vin=vin,
                        model=model,
                        kto_sozdal=request.user.username,
                        data_sozdaniya=timezone.now(),
                    )
                    messages.success(request, "Новая машина успешно создана.")
                    return redirect(f"/?car_id={car.id}")

    return render(request, "defects_app/home.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager,
    })


@permission_required("defects.create")
@station_session_required
def create_defect(request, car_id):
    station_id = request.station_context["station_id"]
    shift_id = request.station_context["shift_id"]

    car = get_object_or_404(Avtomobili, id=car_id)
    from_page = request.GET.get("from_page", "") if request.method == "GET" else request.POST.get("from_page", "")

    if from_page == "okline":
        last_status = get_last_status_for_car(car)
        if last_status and last_status.status == "СГП":
            messages.error(request, "Для машины, уже переданной на СГП, нельзя создавать новые дефекты.")
            return redirect(f"/okline/?car_id={car.id}")

    if from_page == "okline" and station_id != 2:
        return HttpResponseForbidden("У вас нет доступа к созданию дефектов с OKLine.")

    if from_page == "quality" and station_id not in [8, 9, 10]:
        return HttpResponseForbidden("У вас нет доступа к созданию дефектов со станции качества.")

    station_name = request.station_context.get("station_name")

    if from_page == "vh1" and not is_vh1_station(station_id=station_id, station_name=station_name):
        return HttpResponseForbidden("У вас нет доступа к созданию дефектов с ВХ1.")

    if from_page == "dovodka" and station_id != 11:
        return HttpResponseForbidden("У вас нет доступа к созданию дефектов с Доводки.")

    if request.method == "POST":
        form = DefectForm(request.POST, request.FILES)

        if form.is_valid():
            defect, error_code = create_defect_for_car(
                car=car,
                form=form,
                request=request,
                station_id=station_id,
                shift_id=shift_id,
            )

            if error_code == "LOGIN_REQUIRED":
                messages.error(request, "Не найдены станция или смена. Войдите заново.")
                return redirect("login")

            messages.success(request, "Дефект успешно добавлен.")

            if from_page == "okline":
                return redirect(f"/okline/?car_id={car.id}")
            elif from_page == "quality":
                return redirect(f"/quality/?car_id={car.id}")
            elif from_page == "vh1":
                return redirect(f"/vh1/?car_id={car.id}")
            elif from_page == "dovodka":
                return redirect(f"/dovodka/?car_id={car.id}")
            return redirect(f"/?car_id={car.id}")
    else:
        form = DefectForm()

    return render(request, "defects_app/create_defect.html", {
        "form": form,
        "car": car,
        "from_page": from_page,
    })


@login_required
def check_vin(request):
    vin = request.GET.get("vin", "").strip().upper()

    if len(vin) != 17:
        return JsonResponse({"found": False})

    car = get_created_car_by_vin(vin)

    if car:
        return JsonResponse({
            "found": True,
            "car_id": car.id
        })

    return JsonResponse({"found": False})


@permission_required("defects.edit")
def edit_defect(request, defect_id):

    defect = get_object_or_404(Defekty, id=defect_id)
    car = defect.avto
    from_page = request.GET.get("from_page", "") if request.method == "GET" else request.POST.get("from_page", "")

    if request.method == "POST":
        # Берем оригинальные значения из базы ДО валидации формы
        form = DefectForm(request.POST, request.FILES, instance=defect)

        if form.is_valid():
            updated_defect = update_defect_from_form(
                defect=defect,
                form=form,
                request=request,
            )

            messages.success(request, "Изменения по дефекту сохранены.")

            if from_page == "quality":
                return redirect(f"/quality/?car_id={car.id}")

            if from_page == "vh1":
                return redirect(f"/vh1/?car_id={car.id}")

            if from_page == "okline":
                return redirect(f"/okline/?car_id={car.id}")
            
            if from_page == "dovodka":
                return redirect(f"/dovodka/?car_id={car.id}")

            return redirect(f"/?car_id={car.id}")
    else:
        form = DefectForm(instance=defect)

    return render(request, "defects_app/edit_defect.html", {
        "form": form,
        "car": car,
        "defect": defect,
        "from_page": from_page,
    })


@permission_required("defects.delete")
def delete_defect(request, defect_id):

    defect = get_object_or_404(Defekty, id=defect_id)
    car = defect.avto
    from_page = request.GET.get("from_page", "") if request.method == "GET" else request.POST.get("from_page", "")

    if request.method == "POST":
        defect.delete()
        messages.success(request, "Дефект удален.")

        if from_page == "quality":
            return redirect(f"/quality/?car_id={car.id}")

        if from_page == "okline":
            return redirect(f"/okline/?car_id={car.id}")

        if from_page == "vh1":
            return redirect(f"/vh1/?car_id={car.id}")

        return redirect(f"/?car_id={car.id}")

    return render(request, "defects_app/delete_defect.html", {
        "defect": defect,
        "car": car,
        "from_page": from_page,
    })


@permission_required("defects.create")
@station_session_required
def okline_view(request):
    is_manager = can_edit_delete_defects(request.user)
    station_id = request.station_context["station_id"]

    form = CarSearchForm()
    car = None
    defects = []
    status_history = []
    is_sgp_locked = False
    all_verified = False
    snp_defects = []
    sgp_problem_defects = []

    car_id = request.GET.get("car_id")

    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)

        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        defects = get_defects_for_car(car).prefetch_related("snp_comments")
        snp_defects = get_snp_defects_for_car(car)
        sgp_problem_defects = get_sgp_problem_defects_for_car(car)
        last_status = get_last_status_for_car(car)
        status_history = get_status_history_for_car(car)

        if last_status and last_status.status == "СГП":
            is_sgp_locked = True

        all_verified = not defects.exists() or all(
            defect.ustraneno and defect.proveren for defect in defects
        )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = get_created_car_by_vin(vin)

                if car:
                    return redirect(f"/okline/?car_id={car.id}")

                messages.error(request, "Машина с таким VIN не найдена.")

            return render(request, "defects_app/okline.html", {
                "form": form,
                "car": None,
                "defects": [],
                "vin_prefixes": VIN_PREFIXES,
                "is_sgp_locked": False,
                "all_verified": False,
                "is_manager": is_manager,
                "snp_defects": [],
                "sgp_problem_defects": [],
            })

        elif action == "save_checks":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            defects = get_defects_for_car(car)
            verified_ids = request.POST.getlist("verified_defects")

            verified_count = 0

            for defect in defects:
                if defect.ustraneno and not defect.proveren and str(defect.id) in verified_ids:
                    mark_defect_verified(defect, request.user)
                    verified_count += 1

            if verified_count > 0:
                messages.success(request, f"Подтверждено дефектов: {verified_count}.")
            else:
                messages.info(request, "Новых отметок проверки не было.")

            return redirect(f"/okline/?car_id={car.id}")

        elif action == "send_snp":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)
            if not car_passed_bestenevaya(car):
                messages.error(
                    request,
                    "Нельзя отправить машину на СНП. Сначала машина должна пройти Бестеневую."
                )
                return redirect(f"/okline/?car_id={car.id}")

            defects = get_defects_for_car(car)

            last_status = get_last_status_for_car(car)

            if last_status and last_status.status == "СГП":
                messages.error(request, "Машина уже находится в СГП. На СНП её отправить нельзя.")
                return redirect(f"/okline/?car_id={car.id}")

            all_verified_now = not defects.exists() or all(
                defect.ustraneno and defect.proveren
                for defect in defects
            )

            if all_verified_now:
                messages.error(request, "У машины нет неподтвержденных дефектов. На СНП её отправлять нельзя, только на СГП.")
                return redirect(f"/okline/?car_id={car.id}")

            snp_defects = get_snp_defects_for_car(car)

            if snp_defects.exists():
                for defect in snp_defects:
                    comment_text = request.POST.get(f"snp_comment_{defect.id}", "").strip()

                    if not comment_text:
                        messages.error(request, "Для каждого неподтвержденного дефекта нужно указать причину отправки на СНП.")
                        return redirect(f"/okline/?car_id={car.id}")

                for defect in snp_defects:
                    comment_text = request.POST.get(f"snp_comment_{defect.id}", "").strip()

                    add_snp_comment(defect, car, request.user, comment_text)

            reset_count = 0

            for defect in defects:
                if defect.ustraneno and not defect.proveren:
                    defect.ustraneno = False
                    defect.kto_ustranil = None
                    defect.data_ustraneniya = None
                    defect.save()
                    reset_count += 1

            if not last_status or last_status.status != "СНП":
                send_car_to_snp(car, request.user)

            if reset_count > 0:
                messages.success(request, f"Машина передана на СНП. Сброшено отметок устранения: {reset_count}.")
            else:
                messages.success(request, "Машина передана на СНП.")

            return redirect(f"/okline/?car_id={car.id}")

        elif action == "send_sgp":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)
            if not car_passed_bestenevaya(car):
                messages.error(
                    request,
                    "Нельзя отправить машину на СГП. Сначала машина должна пройти Бестеневую."
                )
                return redirect(f"/okline/?car_id={car.id}")

            last_status = StatusAvto.objects.filter(
                avto=car
            ).order_by("-data_statusa").first()

            if last_status and last_status.status == "СГП":
                messages.error(request, "Машина уже находится в СГП.")
                return redirect(f"/okline/?car_id={car.id}")

            problem_defects = get_sgp_problem_defects_for_car(car)

            if problem_defects.exists():
                if not can_edit_delete_defects(request.user):
                    messages.error(
                        request,
                        "Ваших полномочий не хватает, чтобы отправить машину на СГП при неустраненных и(или) непроверенных дефектах. Пожалуйста, обратитесь к старшим."
                    )
                    return redirect(f"/okline/?car_id={car.id}")

                messages.error(
                    request,
                    "У машины есть неустраненные и(или) непроверенные дефекты. Для отправки на СГП необходимо согласование."
                )
                return redirect(f"/okline/?car_id={car.id}")

            send_car_to_sgp(car, request.user)

            messages.success(request, "Машина передана на СГП.")
            return redirect("print_sgp_report", car_id=car.id)

        elif action == "approve_and_send_sgp":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            if not car_passed_bestenevaya(car):
                messages.error(
                    request,
                    "Нельзя отправить машину на СГП. Сначала машина должна пройти Бестеневую."
                )
                return redirect(f"/okline/?car_id={car.id}")

            if not can_edit_delete_defects(request.user):
                messages.error(
                    request,
                    "Ваших полномочий не хватает для согласования дефектов перед отправкой на СГП."
                )
                return redirect(f"/okline/?car_id={car.id}")

            last_status = StatusAvto.objects.filter(
                avto=car
            ).order_by("-data_statusa").first()

            if last_status and last_status.status == "СГП":
                messages.error(request, "Машина уже находится в СГП.")
                return redirect(f"/okline/?car_id={car.id}")

            comment = request.POST.get("approval_comment", "").strip()

            problem_defects = get_sgp_problem_defects_for_car(car)

            if not problem_defects.exists():
                send_car_to_sgp(car, request.user)

                messages.success(request, "Машина передана на СГП.")
                return redirect("print_sgp_report", car_id=car.id)

            approved_count = approve_defects_for_sgp(car, request.user, comment)

            send_car_to_sgp(car, request.user)

            messages.success(
                request,
                f"Согласовано дефектов: {approved_count}. Машина передана на СГП."
            )
            return redirect("print_sgp_report", car_id=car.id)

    return render(request, "defects_app/okline.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "vin_prefixes": VIN_PREFIXES,
        "is_sgp_locked": is_sgp_locked,
        "all_verified": all_verified,
        "is_manager": can_edit_delete_defects(request.user),
        "snp_defects": snp_defects,
        "status_history": status_history,
        "sgp_problem_defects": sgp_problem_defects,
    })


@station_session_required
def print_bestenevaya_defects_view(request, car_id):
    if not (
        has_permission(request.user, "cars.create_print")
        or has_permission(request.user, "defects.create")
    ):
        return HttpResponseForbidden("У вас нет прав печатать дефекты Бестеневой.")

    car = get_object_or_404(Avtomobili, id=car_id)
    defects = get_defects_for_car(car).order_by("data", "id")
    printed_by = request.user.get_full_name() or request.user.username

    return render(request, "defects_app/print_bestenevaya_defects.html", {
        "car": car,
        "defects": defects,
        "printed_at": timezone.now(),
        "printed_by": printed_by,
    })


@station_session_required
def complete_bestenevaya(request, car_id):
    station_id = request.station_context["station_id"]

    if not (
        has_permission(request.user, "cars.create_print")
        or has_permission(request.user, "defects.create")
    ):
        return HttpResponseForbidden("У вас нет прав отмечать прохождение Бестеневой.")

    car = get_object_or_404(Avtomobili, id=car_id)

    if request.method == "POST":
        car.proshla_bestenevaya = True
        car.data_prohoda_bestenevaya = timezone.now()
        car.save(update_fields=["proshla_bestenevaya", "data_prohoda_bestenevaya"])

        messages.success(request, "Машина отмечена как прошедшая станцию Бестеневая.")
        return redirect(f"/?car_id={car.id}")

    return redirect(f"/?car_id={car.id}")

@permission_required("defects.create")
@station_session_required
def quality_view(request):
    station_id = request.station_context["station_id"]
    is_manager = can_edit_delete_defects(request.user)

    form = CarSearchForm()
    car = None
    defects = []

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })
        defects = get_defects_for_car(car)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                existing_car = get_created_car_by_vin(vin)

                if existing_car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/quality/?car_id={existing_car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")
                    return render(request, "defects_app/quality.html", {
                        "form": form,
                        "car": None,
                        "defects": [],
                        "vin_prefixes": VIN_PREFIXES,
                        "is_manager": is_manager,
                    })

    return render(request, "defects_app/quality.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager,
        "from_page": "quality",
    })


@permission_required("defects.create")
@station_session_required
def vh1_view(request):
    station_id = request.station_context["station_id"]
    is_manager = can_edit_delete_defects(request.user)

    station_name = request.station_context.get("station_name")

    if not is_vh1_station(station_id=station_id, station_name=station_name):
        return HttpResponseForbidden("Для вашей станции эта форма недоступна.")

    form = CarSearchForm()
    car = None
    defects = []

    latest_receipts = get_latest_container_receipts()    
    container_car_link = None

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })
        defects = get_defects_for_car(car)
        container_car_link = ContainerCar.objects.filter(
            avto=car
        ).select_related(
            "receipt",
            "receipt__container"
        ).order_by("-accepted_at").first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                existing_car = get_car_by_vin(vin)

                if existing_car:
                    messages.success(request, "Машина найдена.")
                    return redirect(f"/vh1/?car_id={existing_car.id}")

                plan_vin = PlanovyeVin.objects.filter(vin=vin).first()
                if not plan_vin:
                    messages.error(request, "Машина с таким VIN не найдена в созданных и плановых VIN.")
                    return render(request, "defects_app/quality.html", {
                        "form": form,
                        "car": None,
                        "defects": [],
                        "vin_prefixes": VIN_PREFIXES,
                        "is_manager": is_manager,
                        "from_page": "vh1",
                        "latest_receipts": latest_receipts,
                    })

                model_name = plan_vin.model.strip()
                model_obj, _ = Modeli.objects.get_or_create(nazvanie=model_name)

                created_car = Avtomobili.objects.create(
                    vin=vin,
                    model=model_obj,
                    kto_sozdal=request.user.username,
                    data_sozdaniya=timezone.now(),
                    created_on_station_1=False,
                )
                messages.success(request, "Машина найдена в плановых VIN и создана для ВХ1.")
                return redirect(f"/vh1/?car_id={created_car.id}")
            

        elif action == "bind_container":
            car_id_post = request.POST.get("car_id")
            receipt_id = request.POST.get("receipt_id")

            car = get_object_or_404(Avtomobili, id=car_id_post)
            receipt = get_object_or_404(ContainerReceipt, id=receipt_id)

            existing_link = ContainerCar.objects.filter(
                receipt=receipt,
                avto=car,
            ).first()

            if existing_link:
                messages.info(request, "Эта машина уже привязана к выбранной приемке контейнера.")
            else:
                ContainerCar.objects.create(
                    receipt=receipt,
                    avto=car,
                    accepted_by=request.user.username,
                )
                messages.success(request, "Машина привязана к приемке контейнера и принята на ВХ1.")

            return redirect(f"/vh1/?car_id={car.id}")
    linked_receipt = None

    if car:
        linked_container_car = ContainerCar.objects.filter(
            avto=car
        ).select_related("receipt").first()

        if linked_container_car:
            linked_receipt = linked_container_car.receipt

    return render(request, "defects_app/quality.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager,
        "from_page": "vh1",
        "latest_receipts": latest_receipts,
        "container_car_link": container_car_link,
        "linked_receipt": linked_receipt,
    })


@permission_required("defects.create")
@station_session_required
def dovodka_view(request):
    is_manager = is_manager_user(request.user)
    station_id = request.station_context["station_id"]

    form = CarSearchForm()
    car = None
    defects = []
    snp_defects = []
    status_history = []
    all_verified = False

    car_id = request.GET.get("car_id")
    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)
        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })
        defects = get_defects_for_car(car).prefetch_related("snp_comments")

        snp_defects = get_unfixed_defects_for_car(car)
        status_history = get_status_history_for_car(car)

        all_verified = defects.exists() and all(defect.proveren for defect in defects)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)
            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = get_created_car_by_vin(vin)

                if car:
                    return redirect(f"/dovodka/?car_id={car.id}")
                else:
                    messages.error(request, "Машина с таким VIN не найдена.")

        elif action == "save_repairs":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)

            defects = Defekty.objects.filter(avto=car).order_by("-data")
            fixed_ids = request.POST.getlist("fixed_defects")

            fixed_count = 0

            for defect in defects:
                if not defect.ustraneno and str(defect.id) in fixed_ids:
                    mark_defect_fixed(defect, request.user)
                    fixed_count += 1

            if fixed_count > 0:
                messages.success(request, f"Отмечено устраненных дефектов: {fixed_count}.")
            else:
                messages.info(request, "Новых отметок устранения не было.")

            return redirect(f"/dovodka/?car_id={car.id}")
        
        elif action == "send_snp":
            car_id_post = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id_post)
            defects = get_defects_for_car(car)

            if not car_passed_bestenevaya(car):
                messages.error(
                    request,
                    "Нельзя отправить машину на СНП. Сначала машина должна пройти Бестеневую."
                )
                return redirect(f"/dovodka/?car_id={car.id}")

            last_status = get_last_status_for_car(car)

            if last_status and last_status.status == "СГП":
                messages.error(request, "Машина уже находится в СГП. На СНП её отправить нельзя.")
                return redirect(f"/dovodka/?car_id={car.id}")

            all_verified = defects.exists() and all(defect.proveren for defect in defects)
            if all_verified:
                messages.error(request, "Машина уже полностью проверена. На СНП её отправлять нельзя.")
                return redirect(f"/dovodka/?car_id={car.id}")

            snp_defects = get_unfixed_defects_for_car(car)

            if snp_defects.exists():
                has_empty_comment = False

                for defect in snp_defects:
                    comment_text = request.POST.get(f"snp_comment_{defect.id}", "").strip()

                    if not comment_text:
                        has_empty_comment = True
                        break

                if has_empty_comment:
                    messages.error(request, "Для каждого неустраненного дефекта нужно указать причину отправки на СНП.")
                    return redirect(f"/dovodka/?car_id={car.id}")

                for defect in snp_defects:
                    comment_text = request.POST.get(f"snp_comment_{defect.id}", "").strip()

                    add_snp_comment(defect, car, request.user, comment_text)

            send_car_to_snp(car, request.user)

            messages.success(request, "Машина передана на СНП.")

            return redirect(f"/dovodka/?car_id={car.id}")

    return render(request, "defects_app/dovodka.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "vin_prefixes": VIN_PREFIXES,
        "is_manager": is_manager_user(request.user),
        "snp_defects": snp_defects,
        "status_history": status_history,
        "all_verified": all_verified
    })

@login_required
def snp_orders_view(request):
    session_data, redirect_response = require_station_session(request)
    if redirect_response:
        return redirect_response

    is_manager = is_manager_user(request.user)

    form = CarSearchForm()
    car = None
    defects = []
    message_text = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "find":
            form = CarSearchForm(request.POST)

            if form.is_valid():
                vin = form.cleaned_data["vin"]
                car = get_created_car_by_vin(vin)

                if not car:
                    messages.error(request, "Машина с таким VIN не найдена.")
                    return redirect("snp_orders")

                last_status = get_last_status_for_car(car)

                if not last_status or last_status.status != "СНП":
                    messages.error(request, "Эта машина сейчас не находится на СНП. Ввод номеров заказов недоступен.")
                    return redirect("snp_orders")

                return redirect(f"/snp-orders/?car_id={car.id}")

        elif action == "save_orders":
            car_id = request.POST.get("car_id")
            car = get_object_or_404(Avtomobili, id=car_id)

            last_status = get_last_status_for_car(car)

            if not last_status or last_status.status != "СНП":
                messages.error(request, "Сохранять заказы можно только для машины, которая сейчас находится на СНП.")
                return redirect("snp_orders")

            defects = Defekty.objects.filter(avto=car).prefetch_related("snp_order")

            saved_count = 0
            updated_count = 0

            for defect in defects:
                if defect.ustraneno:
                    continue

                order_number = request.POST.get(f"order_{defect.id}", "").strip()

                if not order_number:
                    continue

                existing_order = getattr(defect, "snp_order", None)

                if existing_order:
                    if not can_edit_delete_defects(request.user):
                        continue

                    if existing_order.order_number != order_number:
                        existing_order.order_number = order_number
                        existing_order.kto_izmenil = request.user.username
                        existing_order.data_izmeneniya = timezone.now()
                        existing_order.save()
                        updated_count += 1
                else:
                    SnpDefectOrder.objects.create(
                        defect=defect,
                        avto=car,
                        order_number=order_number,
                        kto_sozdal=request.user.username,
                    )
                    saved_count += 1

            messages.success(request, f"Сохранено новых заказов: {saved_count}. Изменено заказов: {updated_count}.")
            return redirect(f"/snp-orders/?car_id={car.id}")

    car_id = request.GET.get("car_id")

    if car_id:
        car = get_object_or_404(Avtomobili, id=car_id)

        last_status = get_last_status_for_car(car)

        if not last_status or last_status.status != "СНП":
            messages.error(request, "Эта машина сейчас не находится на СНП. Ввод номеров заказов недоступен.")
            return redirect("snp_orders")

        form = CarSearchForm(initial={
            "vin": car.vin,
            "model": car.model
        })

        defects = Defekty.objects.filter(avto=car).select_related(
            "tip",
            "oblast",
            "greyd",
            "otvetstvennyj",
            "mesto"
        ).prefetch_related(
            "snp_order"
        ).order_by("id")

    return render(request, "defects_app/snp_orders.html", {
        "form": form,
        "car": car,
        "defects": defects,
        "is_manager": is_manager,
        "vin_prefixes": VIN_PREFIXES,
    })