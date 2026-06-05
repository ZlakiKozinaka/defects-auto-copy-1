import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from defects_app.forms import ContainerReceiptForm

from defects_app.models import (
    Container,
    ContainerReceipt,
    ContainerSeal,
    ContainerCar,
    Defekty,
    PlanovyeVin,
)
from defects_app.services.photo_service import (
    save_container_receipt_photos,
    save_container_car_photos,
)


@login_required
def container_receipts_view(request):
    today = timezone.now().date()
    form = ContainerReceiptForm()

    latest_receipts = ContainerReceipt.objects.select_related(
        "container"
    ).order_by("-created_at")[:10]

    search_results = []
    search_container_number = ""
    search_month = today.strftime("%Y-%m")
    search_was_submitted = False

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = ContainerReceiptForm(request.POST, request.FILES)

            if form.is_valid():
                submission_token = request.POST.get("submission_token") or uuid.uuid4().hex
                existing_receipt = ContainerReceipt.objects.filter(
                    submission_token=submission_token
                ).first()

                if existing_receipt:
                    messages.info(
                        request,
                        f"Эта приемка уже сохраняется или сохранена. Акт №{existing_receipt.daily_number}."
                    )
                    return redirect("container_receipt_detail", receipt_id=existing_receipt.id)
                
                container_number = form.cleaned_data["container_number"]
                seals_text = form.cleaned_data.get("seals_text", "")

                try:
                    with transaction.atomic():
                        container, _ = Container.objects.get_or_create(
                            number=container_number,
                            defaults={"is_active": True}
                        )

                        max_number = ContainerReceipt.objects.filter(
                            receipt_date=today
                        ).aggregate(
                            max_number=Max("daily_number")
                        )["max_number"] or 0

                        receipt = form.save(commit=False)
                        receipt.container = container
                        receipt.receipt_date = today
                        receipt.daily_number = max_number + 1
                        receipt.created_by = request.user.username
                        receipt.submission_token = submission_token
                        receipt.save()

                        seals = [
                            item.strip()
                            for item in seals_text.replace(";", ",").split(",")
                            if item.strip()
                        ]

                        for seal in seals:
                            ContainerSeal.objects.create(
                                receipt=receipt,
                                seal_number=seal
                            )
                except IntegrityError:
                    existing_receipt = ContainerReceipt.objects.filter(
                        submission_token=submission_token
                    ).first()

                    if existing_receipt:
                        messages.info(
                            request,
                            f"Эта приемка уже сохраняется или сохранена. Акт №{existing_receipt.daily_number}."
                        )
                        return redirect("container_receipt_detail", receipt_id=existing_receipt.id)

                    raise

                save_container_receipt_photos(receipt, request)

                messages.success(
                    request,
                    f"Приемка контейнера сохранена. Акт №{receipt.daily_number}."
                )
                return redirect("container_receipts")

        elif action == "search":
            search_was_submitted = True
            search_container_number = request.POST.get("search_container_number", "").strip().upper()
            search_month = request.POST.get("search_month", today.strftime("%Y-%m"))

            receipts = ContainerReceipt.objects.select_related("container").order_by("-receipt_date", "-created_at")

            if search_container_number:
                receipts = receipts.filter(container__number__icontains=search_container_number)

            if search_month:
                year, month = search_month.split("-")
                receipts = receipts.filter(
                    receipt_date__year=int(year),
                    receipt_date__month=int(month),
                )

            search_results = receipts

    return render(request, "defects_app/container_receipts.html", {
        "form": form,
        "today": today,
        "latest_receipts": latest_receipts,
        "search_results": search_results,
        "search_container_number": search_container_number,
        "search_month": search_month,
        "search_was_submitted": search_was_submitted,
    })


@login_required
def container_receipt_detail_view(request, receipt_id):
    receipt = get_object_or_404(
        ContainerReceipt.objects.select_related("container").prefetch_related("seals", "photos"),
        id=receipt_id
    )

    container_cars = ContainerCar.objects.filter(
        receipt=receipt
    ).select_related(
        "avto",
        "avto__model",
    ).prefetch_related(
        "photos",
        "avto__defekty_set",
    ).order_by("id")

    rows = []

    for item in container_cars:
        car = item.avto

        plan_vin = PlanovyeVin.objects.filter(
            vin=car.vin
        ).first()

        defects = Defekty.objects.filter(
            avto=car
        ).select_related(
            "tip",
            "oblast",
            "greyd",
            "otvetstvennyj",
        ).order_by("data")

        defect_descriptions = []

        for defect in defects:
            defect_descriptions.append(
                f"{defect.tip} / {defect.oblast} / {defect.greyd}"
            )

        rows.append({
            "container_car": item,
            "car": car,
            "plan_vin": plan_vin,
            "photos": item.photos.all(),
            "defects": defects,
            "defects_count": defects.count(),
            "defect_descriptions": "; ".join(defect_descriptions),
        })

    return render(request, "defects_app/container_receipt_detail.html", {
        "receipt": receipt,
        "rows": rows,
    })


@login_required
def upload_container_car_photos_view(request, container_car_id):
    container_car = get_object_or_404(
        ContainerCar.objects.select_related("receipt", "avto"),
        id=container_car_id
    )

    if request.method == "POST":
        save_container_car_photos(container_car, request)
        messages.success(request, "Фото приемки машины загружены.")
        return redirect(f"/vh1/?car_id={container_car.avto.id}")

    return redirect(f"/vh1/?car_id={container_car.avto.id}")


@login_required
def print_container_receipt_view(request, receipt_id):
    receipt = get_object_or_404(
        ContainerReceipt.objects.select_related("container").prefetch_related("seals"),
        id=receipt_id
    )

    container_cars = ContainerCar.objects.filter(
        receipt=receipt
    ).select_related(
        "avto",
        "avto__model",
    ).order_by("id")

    rows = []

    for item in container_cars:
        car = item.avto

        plan_vin = PlanovyeVin.objects.filter(vin=car.vin).first()

        defects = Defekty.objects.filter(
            avto=car
        ).select_related(
            "tip",
            "oblast",
            "greyd",
        ).order_by("data")

        defect_descriptions = []

        for defect in defects:
            defect_descriptions.append(
                f"{defect.tip} / {defect.oblast} / {defect.greyd}"
            )

        rows.append({
            "number": len(rows) + 1,
            "car": car,
            "plan_vin": plan_vin,
            "defect_descriptions": "; ".join(defect_descriptions),
        })

    return render(request, "defects_app/print_container_receipt.html", {
        "receipt": receipt,
        "rows": rows,
    })