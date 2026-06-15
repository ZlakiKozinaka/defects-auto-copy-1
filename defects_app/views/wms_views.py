from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from defects_app.services.wms_issue import WmsIssueError, issue_box_item
from functools import wraps
import barcode
from barcode.writer import SVGWriter
from io import BytesIO

from defects_app.permissions import (
    has_wms_site_permission,
    is_global_manager,
)
from defects_app.forms_wms import (
    WmsCaseSuggestedPlacementForm,
    WmsCaseManualPlacementForm,
    WmsContainerPlacementForm,
    WmsContainerSearchForm,
    WmsLotScanForm,
    WmsLotUploadForm,
    WmsStorageLineCreateForm,
)
from defects_app.models import (
    WmsBoxItem,
    WmsBox,
    WmsContainer,
    WmsCase,
    WmsLot,
    WmsPallet,
    WmsPalletPlacement,
    WmsStorageUnit,
    WmsStorageCell,
    WmsStorageLine,
    WmsPalletType,
    WmsSite,
    WmsWarehouse,
)
from defects_app.services.wms_import import import_wms_lot_from_excel
from defects_app.services.wms_storage import (
    WmsStorageError,
    get_cell_occupancy,
    get_position_choices_for_pallet_type,
    place_pallet,
    remove_pallet,
    suggest_best_places_for_pallet_type,
)

def get_wms_site_or_404(site_code):
    return get_object_or_404(
        WmsSite,
        code__iexact=site_code,
        is_active=True,
    )

def get_wms_menu_context(request, site):
    site_code = site.code.lower()

    return {
        "can_access_gzhel": has_wms_site_permission(request.user, "gzhel", "view"),
        "can_access_lipetsk": has_wms_site_permission(request.user, "lipetsk", "view"),

        "can_import_current_wms": has_wms_site_permission(request.user, site_code, "import"),
        "can_edit_current_wms_map": has_wms_site_permission(request.user, site_code, "map_edit"),
        "can_cancel_current_wms": has_wms_site_permission(request.user, site_code, "cancel"),

        "can_see_defects_link": is_global_manager(request.user),
    }

def wms_site_permission_required(action):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, site_code, *args, **kwargs):
            if is_global_manager(request.user):
                return view_func(request, site_code, *args, **kwargs)

            if not has_wms_site_permission(request.user, site_code, action):
                return render(request, "403.html", {
                    "access_denied_message": "У вас нет доступа к этому складу или действию.",
                }, status=403)

            return view_func(request, site_code, *args, **kwargs)

        return wrapper
    return decorator

@login_required
@wms_site_permission_required("view")
def wms_home_view(request, site_code):
    site = get_wms_site_or_404(site_code)
    lot_scan_form = WmsLotScanForm()
    container_search_form = WmsContainerSearchForm(request.GET or None)
    container_results = []

    if container_search_form.is_valid() and container_search_form.cleaned_data.get("container_number"):
        container_results = WmsContainer.objects.filter(
            lot__site=site,
            container_number__icontains=container_search_form.cleaned_data["container_number"]
        ).select_related("lot").order_by("lot__lot_number", "container_number")[:20]

    latest_lots = WmsLot.objects.filter(site=site).annotate(
        containers_total=Count("containers", distinct=True),
    ).order_by("-uploaded_at")[:10]

    return render(request, "defects_app/wms/home.html", {
        "lot_scan_form": lot_scan_form,
        "container_search_form": container_search_form,
        "container_results": container_results,
        "latest_lots": latest_lots,
        "site": site,
        "site_code": site.code.lower(),
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("view")
def wms_global_search_view(request, site_code):
    site = get_wms_site_or_404(site_code)

    query = request.GET.get("q", "").strip()
    query_upper = query.upper()

    lots = []
    containers = []
    cases = []
    boxes = []
    items = []
    cells = []

    if query:
        lots = WmsLot.objects.filter(
            site=site,
            is_active=True,
        ).filter(
            Q(lot_number__icontains=query)
            | Q(display_name__icontains=query)
            | Q(comment__icontains=query)
        ).annotate(
            containers_total=Count("containers", distinct=True),
        ).order_by("-uploaded_at")[:30]

        containers = WmsContainer.objects.filter(
            lot__site=site,
            is_active=True,
        ).filter(
            Q(container_number__icontains=query)
            | Q(seal_number__icontains=query)
            | Q(comment__icontains=query)
            | Q(lot__lot_number__icontains=query)
        ).select_related(
            "lot",
        ).order_by("lot__lot_number", "container_number")[:50]

        cases = WmsCase.objects.filter(
            container__lot__site=site,
            is_active=True,
        ).filter(
            Q(case_number__icontains=query)
            | Q(container__container_number__icontains=query)
            | Q(container__lot__lot_number__icontains=query)
        ).select_related(
            "container",
            "container__lot",
        ).order_by("container__lot__lot_number", "container__container_number", "case_number")[:50]

        boxes = WmsBox.objects.filter(
            case__container__lot__site=site,
            is_active=True,
        ).filter(
            Q(box_number__icontains=query)
            | Q(case__case_number__icontains=query)
            | Q(case__container__container_number__icontains=query)
            | Q(case__container__lot__lot_number__icontains=query)
        ).select_related(
            "case",
            "case__container",
            "case__container__lot",
        ).order_by(
            "case__container__lot__lot_number",
            "case__container__container_number",
            "case__case_number",
            "box_number",
        )[:50]

        raw_items = WmsBoxItem.objects.filter(
            box__case__container__lot__site=site,
            is_active=True,
        ).filter(
            Q(part_number__icontains=query)
            | Q(chinese_name__icontains=query)
            | Q(chinese_description__icontains=query)
            | Q(english_name__icontains=query)
            | Q(english_description__icontains=query)
            | Q(box__box_number__icontains=query)
            | Q(box__case__case_number__icontains=query)
            | Q(box__case__container__container_number__icontains=query)
            | Q(box__case__container__lot__lot_number__icontains=query)
        ).select_related(
            "box",
            "box__case",
            "box__case__container",
            "box__case__container__lot",
        ).order_by(
            "part_number",
            "box__case__container__lot__lot_number",
            "box__case__container__container_number",
            "box__case__case_number",
            "box__box_number",
        )[:100]

        for item in raw_items:
            box = item.box
            case = box.case
            container = case.container

            active_placement = WmsPalletPlacement.objects.filter(
                is_active=True,
            ).filter(
                Q(pallet__storage_unit__box=box)
                | Q(pallet__storage_unit__case=case)
                | Q(pallet__storage_unit__container=container)
            ).select_related(
                "cell",
                "cell__line",
                "pallet",
                "pallet__storage_unit",
            ).first()

            placement_text = "Не размещено"
            placement_type = "—"

            if active_placement:
                placement_text = (
                    f"{active_placement.cell.address} "
                    f"[{active_placement.position_from}-{active_placement.position_to}]"
                )

                storage_unit = active_placement.pallet.storage_unit

                if storage_unit.box_id:
                    placement_type = "Размещена коробка"
                elif storage_unit.case_id:
                    placement_type = "Размещен кейс"
                elif storage_unit.container_id:
                    placement_type = "Размещен контейнер"

            items.append({
                "item": item,
                "lot": container.lot,
                "container": container,
                "case": case,
                "box": box,
                "placement_text": placement_text,
                "placement_type": placement_type,
            })

        cells_query = WmsStorageCell.objects.filter(
            line__warehouse__site=site,
        ).select_related(
            "line",
            "line__warehouse",
        )

        if ";" in query_upper:
            line_part = query_upper.split(";")[0]
            level_part = query_upper.split(";")[1]

            line_code = "".join([ch for ch in line_part if ch.isalpha()])
            column_raw = "".join([ch for ch in line_part if ch.isdigit()])
            level_raw = "".join([ch for ch in level_part if ch.isdigit()])

            if line_code:
                cells_query = cells_query.filter(line__code__iexact=line_code)

            if column_raw:
                cells_query = cells_query.filter(column_number=int(column_raw))

            if level_raw:
                cells_query = cells_query.filter(level_number=int(level_raw))
        else:
            cells_query = cells_query.filter(
                Q(line__code__icontains=query)
                | Q(line__warehouse__code__icontains=query)
                | Q(line__warehouse__name__icontains=query)
                | Q(comment__icontains=query)
            )

        for cell in cells_query.order_by(
            "line__sort_order",
            "line__code",
            "column_number",
            "level_number",
        )[:50]:
            cells.append({
                "cell": cell,
                "occupancy": get_cell_occupancy(cell),
            })

    total_results = (
        len(lots)
        + len(containers)
        + len(cases)
        + len(boxes)
        + len(items)
        + len(cells)
    )

    return render(request, "defects_app/wms/search_results.html", {
        "site": site,
        "site_code": site.code.lower(),
        "query": query,
        "lots": lots,
        "containers": containers,
        "cases": cases,
        "boxes": boxes,
        "items": items,
        "cells": cells,
        "total_results": total_results,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("import")
def wms_lot_upload_view(request, site_code):
    site = get_wms_site_or_404(site_code)

    result = None

    if request.method == "POST":
        form = WmsLotUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                result = import_wms_lot_from_excel(
                    form.cleaned_data["source_file"],
                    form.cleaned_data["lot_number"],
                    request.user,
                    form.cleaned_data["comment"],
                    site=site,
                )

                messages.success(request, f"Лот {result.lot.lot_number} загружен.")
                return redirect(
                    "wms_lot_detail",
                    site_code=site.code.lower(),
                    lot_id=result.lot.id,
                )

            except Exception as exc:
                messages.error(request, f"Ошибка загрузки WMS Excel: {exc}")
    else:
        form = WmsLotUploadForm()

    return render(request, "defects_app/wms/lot_upload.html", {
        "form": form,
        "result": result,
        "site": site,
        "site_code": site.code.lower(),
        **get_wms_menu_context(request, site),
    })


@login_required
@wms_site_permission_required("view")
def wms_lot_detail_view(request, site_code, lot_id):
    site = get_wms_site_or_404(site_code)

    lot = get_object_or_404(
        WmsLot,
        id=lot_id,
        site=site,
    )

    query = request.GET.get("q", "").strip()

    containers = WmsContainer.objects.filter(
        lot=lot,
    ).order_by("container_number")

    matched_case_ids = []
    matched_container_ids = []

    if query:
        matched_container_ids = list(
            WmsContainer.objects.filter(lot=lot).filter(
                Q(container_number__contains=query)
                | Q(cases__case_number__contains=query)
                | Q(cases__boxes__box_number__contains=query)
                | Q(cases__boxes__items__part_number__contains=query)
            ).values_list("id", flat=True).distinct()
        )

        matched_case_ids = list(
            WmsCase.objects.filter(container__lot=lot).filter(
                Q(case_number__contains=query)
                | Q(boxes__box_number__contains=query)
                | Q(boxes__items__part_number__contains=query)
            ).values_list("id", flat=True).distinct()
        )

        containers = containers.filter(id__in=matched_container_ids)

    totals = {
        "containers": WmsContainer.objects.filter(lot=lot).count(),
        "items": WmsBoxItem.objects.filter(box__case__container__lot=lot).count(),
    }

    return render(request, "defects_app/wms/lot_detail.html", {
        "site": site,
        "site_code": site.code.lower(),
        "lot": lot,
        "containers": containers,
        "query": query,
        "totals": totals,
        "matched_case_ids": matched_case_ids,
        "matched_container_ids": matched_container_ids,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("view")
def wms_container_cases_api_view(request, site_code, container_id):
    site = get_wms_site_or_404(site_code)

    container = get_object_or_404(
        WmsContainer.objects.select_related("lot", "lot__site"),
        id=container_id,
        lot__site=site,
    )

    cases = WmsCase.objects.filter(
        container=container,
        is_active=True,
    ).prefetch_related(
        "boxes",
        "storage_units__pallets__placements__cell__line",
    ).order_by("case_number")

    data = []

    for case in cases:
        active_place = None

        for storage_unit in case.storage_units.all():
            for pallet in storage_unit.pallets.all():
                for placement in pallet.placements.all():
                    if placement.is_active:
                        active_place = {
                            "cell": placement.cell.address,
                            "position_from": placement.position_from,
                            "position_to": placement.position_to,
                        }
                        break

        data.append({
            "id": case.id,
            "container_id": container.id,
            "case_number": case.case_number,
            "boxes_count": case.boxes.count(),
            "box_numbers": [box.box_number for box in case.boxes.all()],
            "active_place": active_place,
            "place_url": f"/wms/{site.code.lower()}/cases/{case.id}/place/",
            "issue_url": f"/wms/{site.code.lower()}/cases/{case.id}/issue/",
        })

    return JsonResponse({
        "container": {
            "id": container.id,
            "container_number": container.container_number,
            "lot_number": container.lot.lot_number,
        },
        "cases": data,
    })


@login_required
@wms_site_permission_required("view")
def wms_case_details_api_view(request, site_code, case_id):
    site = get_wms_site_or_404(site_code)

    case = get_object_or_404(
        WmsCase.objects.select_related(
            "container",
            "container__lot",
            "container__lot__site",
        ).prefetch_related("boxes__items"),
        id=case_id,
        container__lot__site=site,
    )

    boxes = []

    for box in case.boxes.filter(is_active=True):
        boxes.append({
            "box_number": box.box_number,
            "items": [
                {
                    "part_number": item.part_number,
                    "quantity": str(item.quantity),
                    "unit": item.unit or "—",
                    "description": f"{item.english_name or ''} {item.chinese_name or ''}".strip(),
                }
                for item in box.items.filter(is_active=True)
            ],
        })

    return JsonResponse({
        "case": {
            "id": case.id,
            "case_number": case.case_number,
            "container_number": case.container.container_number,
            "lot_number": case.container.lot.lot_number,
        },
        "boxes": boxes,
    })

@login_required
@wms_site_permission_required("view")
def wms_lot_scan_view(request, site_code):
    site = get_wms_site_or_404(site_code)

    form = WmsLotScanForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        lot_number = form.cleaned_data["lot_number"]

        lot = WmsLot.objects.filter(
            site=site,
            lot_number__iexact=lot_number,
        ).first()

        if lot:
            return redirect(
                "wms_lot_detail",
                site_code=site.code.lower(),
                lot_id=lot.id,
            )

        messages.error(request, f"Лот {lot_number} не найден на площадке {site.name}.")

    return render(request, "defects_app/wms/lot_scan.html", {
        "site": site,
        "site_code": site.code.lower(),
        "form": form,
        **get_wms_menu_context(request, site),
    })


@login_required
@wms_site_permission_required("place")
def wms_container_place_view(request, site_code, container_id):
    site = get_wms_site_or_404(site_code)

    container = get_object_or_404(
        WmsContainer.objects.select_related("lot", "lot__site"),
        id=container_id,
        lot__site=site,
    )

    if request.method == "POST":
        form = WmsContainerPlacementForm(request.POST)

        if form.is_valid():
            position_from, position_to = form.cleaned_data["position"]

            try:
                with transaction.atomic():
                    storage_unit, _ = WmsStorageUnit.objects.get_or_create(
                        unit_type=WmsStorageUnit.UNIT_CONTAINER,
                        container=container,
                        defaults={
                            "label": container.container_number,
                            "created_by": request.user.username,
                            "is_active": True,
                        },
                    )

                    pallet = WmsPallet.objects.create(
                        pallet_type=form.cleaned_data["pallet_type"],
                        pallet_number=form.cleaned_data["pallet_number"],
                        storage_unit=storage_unit,
                        comment=form.cleaned_data["comment"],
                        created_by=request.user.username,
                    )

                    placement = place_pallet(
                        pallet,
                        form.cleaned_data["cell"],
                        position_from,
                        position_to,
                        request.user,
                    )

                messages.success(
                    request,
                    f"Контейнер размещен: {placement.cell.address} "
                    f"[{placement.position_from}-{placement.position_to}]."
                )

                return redirect(
                    "wms_cell_detail",
                    site_code=site.code.lower(),
                    cell_id=placement.cell.id,
                )

            except WmsStorageError as exc:
                messages.error(request, str(exc))
    else:
        form = WmsContainerPlacementForm()

    selected_cell = None
    occupancy = None
    position_choices = []

    cell_id = request.POST.get("cell") or request.GET.get("cell")
    pallet_type_id = request.POST.get("pallet_type") or request.GET.get("pallet_type")

    if cell_id:
        selected_cell = WmsStorageCell.objects.filter(
            id=cell_id,
            line__warehouse__site=site,
        ).select_related("line", "line__warehouse").first()

        if selected_cell:
            occupancy = get_cell_occupancy(selected_cell)

    if selected_cell and pallet_type_id:
        pallet_type = form.fields["pallet_type"].queryset.filter(id=pallet_type_id).first()

        if pallet_type:
            position_choices = get_position_choices_for_pallet_type(selected_cell, pallet_type)

    return render(request, "defects_app/wms/container_place.html", {
        "site": site,
        "site_code": site.code.lower(),
        "container": container,
        "form": form,
        "selected_cell": selected_cell,
        "occupancy": occupancy,
        "position_choices": position_choices,
        **get_wms_menu_context(request, site),
    })

def find_wms_cell_by_address(site, address):
    value = (address or "").strip().upper()
    value = value.replace("А", "A").replace("В", "B").replace("С", "C")
    value = value.replace("-", ";").replace("/", ";").replace("\\", ";").replace(" ", "")

    if ";" not in value:
        raise WmsStorageError("Адрес ячейки должен быть в формате A1;1.")

    left_part, level_part = value.split(";", 1)

    line_code = "".join(ch for ch in left_part if ch.isalpha())
    column_raw = "".join(ch for ch in left_part if ch.isdigit())
    level_raw = "".join(ch for ch in level_part if ch.isdigit())

    if not line_code or not column_raw or not level_raw:
        raise WmsStorageError("Не удалось распознать ячейку. Нужен формат A1;1.")

    cell = WmsStorageCell.objects.filter(
        line__warehouse__site=site,
        line__code__iexact=line_code,
        column_number=int(column_raw),
        level_number=int(level_raw),
    ).select_related(
        "line",
        "line__warehouse",
        "line__warehouse__site",
    ).first()

    if not cell:
        raise WmsStorageError(f"Ячейка {value} не найдена на складе {site.name}.")

    return cell

@login_required
@wms_site_permission_required("place")
def wms_case_place_view(request, site_code, case_id):
    site = get_wms_site_or_404(site_code)

    case = get_object_or_404(
        WmsCase.objects.select_related(
            "container",
            "container__lot",
            "container__lot__site",
        ),
        id=case_id,
        container__lot__site=site,
    )

    selected_pallet_type_id = (
        request.POST.get("pallet_type")
        or request.GET.get("pallet_type")
    )

    if selected_pallet_type_id:
        selected_pallet_type = WmsPalletType.objects.filter(
            id=selected_pallet_type_id,
            is_active=True,
        ).first()
    else:
        selected_pallet_type = WmsPalletType.objects.filter(
            is_active=True,
        ).order_by("name").first()

    suggestions = []

    if selected_pallet_type:
        suggestions = suggest_best_places_for_pallet_type(
            selected_pallet_type,
            base_line_code="A",
            base_column=1,
            base_level=1,
            limit=3,
            site=site,
        )

    if request.method == "POST":
        action = request.POST.get("action", "suggested")

        already_placed = WmsPalletPlacement.objects.filter(
            pallet__storage_unit__case=case,
            is_active=True,
        ).select_related("cell").first()

        if already_placed:
            messages.error(
                request,
                f"Кейс {case.case_number} уже размещён: {already_placed.cell.address} "
                f"[{already_placed.position_from}-{already_placed.position_to}]."
            )
            return redirect(
                "wms_cell_detail",
                site_code=site.code.lower(),
                cell_id=already_placed.cell.id,
            )

        if action == "manual":
            form = WmsCaseManualPlacementForm(request.POST)

            if form.is_valid():
                try:
                    cell = find_wms_cell_by_address(
                        site,
                        form.cleaned_data["cell_address"],
                    )

                    position_choices = get_position_choices_for_pallet_type(
                        cell,
                        form.cleaned_data["pallet_type"],
                    )

                    real_choices = [
                        choice for choice in position_choices
                        if choice[0]
                    ]

                    if not real_choices:
                        raise WmsStorageError("В этой ячейке нет свободного места для выбранного типа поддона.")

                    position_raw = real_choices[0][0]
                    position_from, position_to = map(int, position_raw.split("-"))

                    with transaction.atomic():
                        storage_unit, _ = WmsStorageUnit.objects.get_or_create(
                            unit_type=WmsStorageUnit.UNIT_CASE,
                            case=case,
                            defaults={
                                "label": case.case_number,
                                "created_by": request.user.username,
                                "is_active": True,
                            },
                        )

                        pallet = WmsPallet.objects.create(
                            pallet_type=form.cleaned_data["pallet_type"],
                            pallet_number=form.cleaned_data["pallet_number"],
                            storage_unit=storage_unit,
                            comment=form.cleaned_data["comment"],
                            created_by=request.user.username,
                        )

                        placement = place_pallet(
                            pallet,
                            cell,
                            position_from,
                            position_to,
                            request.user,
                        )

                    messages.success(
                        request,
                        f"Кейс {case.case_number} размещён вручную: "
                        f"{placement.cell.address} [{placement.position_from}-{placement.position_to}]."
                    )

                    return redirect(
                        "wms_cell_detail",
                        site_code=site.code.lower(),
                        cell_id=placement.cell.id,
                    )

                except WmsStorageError as exc:
                    messages.error(request, str(exc))

        else:
            form = WmsCaseSuggestedPlacementForm(request.POST)

            if form.is_valid():
                cell_id, position_from, position_to = form.cleaned_data["selected_place"]

                cell = get_object_or_404(
                    WmsStorageCell,
                    id=cell_id,
                    line__warehouse__site=site,
                )

                try:
                    with transaction.atomic():
                        storage_unit, _ = WmsStorageUnit.objects.get_or_create(
                            unit_type=WmsStorageUnit.UNIT_CASE,
                            case=case,
                            defaults={
                                "label": case.case_number,
                                "created_by": request.user.username,
                                "is_active": True,
                            },
                        )

                        pallet = WmsPallet.objects.create(
                            pallet_type=form.cleaned_data["pallet_type"],
                            pallet_number=form.cleaned_data["pallet_number"],
                            storage_unit=storage_unit,
                            comment=form.cleaned_data["comment"],
                            created_by=request.user.username,
                        )

                        placement = place_pallet(
                            pallet,
                            cell,
                            position_from,
                            position_to,
                            request.user,
                        )

                    messages.success(
                        request,
                        f"Кейс {case.case_number} размещён: {placement.cell.address} "
                        f"[{placement.position_from}-{placement.position_to}]."
                    )

                    return redirect(
                        "wms_cell_detail",
                        site_code=site.code.lower(),
                        cell_id=placement.cell.id,
                    )

                except WmsStorageError as exc:
                    messages.error(request, str(exc))

    form = WmsCaseSuggestedPlacementForm(
        initial={
            "pallet_type": selected_pallet_type,
        }
    )

    manual_form = WmsCaseManualPlacementForm(
        initial={
            "pallet_type": selected_pallet_type,
        }
    )

    return render(request, "defects_app/wms/case_place.html", {
        "site": site,
        "site_code": site.code.lower(),
        "case": case,
        "container": case.container,
        "lot": case.container.lot,
        "form": form,
        "manual_form": manual_form,
        "selected_pallet_type": selected_pallet_type,
        "suggestions": suggestions,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("issue")
def wms_case_issue_view(request, site_code, case_id):
    site = get_wms_site_or_404(site_code)

    case = get_object_or_404(
        WmsCase.objects.select_related(
            "container",
            "container__lot",
            "container__lot__site",
        ).prefetch_related("boxes__items"),
        id=case_id,
        container__lot__site=site,
    )

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity_raw = request.POST.get("quantity", "").strip()

        if not quantity_raw.isdigit():
            messages.error(request, "Количество должно быть целым числом.")
            return redirect(
                "wms_case_issue",
                site_code=site.code.lower(),
                case_id=case.id,
            )

        quantity = int(quantity_raw)

        if quantity <= 0:
            messages.error(request, "Количество должно быть больше нуля.")
            return redirect(
                "wms_case_issue",
                site_code=site.code.lower(),
                case_id=case.id,
            )

        try:
            result_messages = issue_box_item(item_id, quantity, request.user)

            for text in result_messages:
                messages.success(request, text)

            return redirect(
                "wms_case_issue",
                site_code=site.code.lower(),
                case_id=case.id,
            )

        except WmsIssueError as exc:
            messages.error(request, str(exc))
        except WmsBoxItem.DoesNotExist:
            messages.error(request, "Парт-номер не найден.")

    active_placement = WmsPalletPlacement.objects.filter(
        pallet__storage_unit__case=case,
        is_active=True,
    ).select_related("cell").first()

    return render(request, "defects_app/wms/case_issue.html", {
        "site": site,
        "site_code": site.code.lower(),
        "case": case,
        "container": case.container,
        "lot": case.container.lot,
        "active_placement": active_placement,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("map_edit")
def wms_storage_settings_view(request, site_code):
    site = get_wms_site_or_404(site_code)

    warehouse = WmsWarehouse.objects.filter(
        site=site,
        is_active=True,
    ).order_by("code").first()

    if not warehouse:
        messages.error(request, f"Для площадки {site.name} не создан WMS склад.")
        return redirect("wms_storage_map", site_code=site.code.lower())

    if request.method == "POST":
        form = WmsStorageLineCreateForm(request.POST)

        if form.is_valid():
            line_code = form.cleaned_data["line_code"]
            columns_count = form.cleaned_data["columns_count"]
            levels_count = form.cleaned_data["levels_count"]
            capacity_units = form.cleaned_data["capacity_units"]

            if WmsStorageLine.objects.filter(
                warehouse=warehouse,
                code=line_code,
            ).exists():
                messages.error(request, f"Стеллаж {line_code} уже существует на площадке {site.name}.")
                return redirect("wms_storage_settings", site_code=site.code.lower())

            with transaction.atomic():
                line = WmsStorageLine.objects.create(
                    warehouse=warehouse,
                    code=line_code,
                    name=f"Ряд {line_code}",
                    sort_order=ord(line_code) - ord("A") + 1,
                    is_active=True,
                )

                cells = []

                for column_number in range(1, columns_count + 1):
                    for level_number in range(1, levels_count + 1):
                        cells.append(
                            WmsStorageCell(
                                line=line,
                                column_number=column_number,
                                level_number=level_number,
                                capacity_units=capacity_units,
                                is_active=True,
                            )
                        )

                WmsStorageCell.objects.bulk_create(cells)

            messages.success(
                request,
                f"Стеллаж {line_code} создан: {columns_count} столбцов × {levels_count} этажей."
            )

            return redirect("wms_storage_map", site_code=site.code.lower())
    else:
        form = WmsStorageLineCreateForm()

    lines = []

    for line in WmsStorageLine.objects.filter(
        warehouse=warehouse,
    ).prefetch_related("cells").order_by("sort_order", "code"):
        cells = list(line.cells.all())

        columns_count = max([cell.column_number for cell in cells], default=0)
        levels_count = max([cell.level_number for cell in cells], default=0)

        lines.append({
            "line": line,
            "columns_count": columns_count,
            "levels_count": levels_count,
            "cells_count": len(cells),
        })

    return render(request, "defects_app/wms/storage_settings.html", {
        "site": site,
        "site_code": site.code.lower(),
        "warehouse": warehouse,
        "form": form,
        "lines": lines,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("view")
def wms_storage_map_view(request, site_code):
    site = get_wms_site_or_404(site_code)

    lines = WmsStorageLine.objects.filter(
        warehouse__site=site,
        is_active=True,
        warehouse__is_active=True,
        warehouse__site__is_active=True,
    ).select_related(
        "warehouse",
        "warehouse__site",
    ).prefetch_related("cells").order_by(
        "warehouse__code",
        "sort_order",
        "code",
    )

    map_lines = []

    for line in lines:
        cells_by_level = {}

        for cell in line.cells.all():
            occupancy = get_cell_occupancy(cell)
            cells_by_level.setdefault(cell.level_number, []).append({
                "cell": cell,
                "occupancy": occupancy,
            })

        for level_cells in cells_by_level.values():
            level_cells.sort(key=lambda item: item["cell"].column_number)

        map_lines.append({
            "line": line,
            "levels": dict(sorted(cells_by_level.items(), reverse=True)),
        })

    return render(request, "defects_app/wms/storage_map.html", {
        "site": site,
        "site_code": site.code.lower(),
        "map_lines": map_lines,
        **get_wms_menu_context(request, site),
    })


@login_required
@wms_site_permission_required("view")
def wms_cell_detail_view(request, site_code, cell_id):
    site = get_wms_site_or_404(site_code)

    cell = get_object_or_404(
        WmsStorageCell.objects.select_related("line", "line__warehouse", "line__warehouse__site"),
        id=cell_id,
        line__warehouse__site=site,
    )

    active_occupancy = get_cell_occupancy(cell)

    history = WmsPalletPlacement.objects.filter(
        cell=cell,
    ).select_related(
        "pallet",
        "pallet__pallet_type",
        "pallet__storage_unit",
        "pallet__storage_unit__container",
        "pallet__storage_unit__container__lot",
        "pallet__storage_unit__case",
        "pallet__storage_unit__case__container",
        "pallet__storage_unit__case__container__lot",
        "pallet__storage_unit__box",
        "pallet__storage_unit__box__case",
        "pallet__storage_unit__box__case__container",
        "pallet__storage_unit__box__case__container__lot",
    ).order_by("-placed_at")

    return render(request, "defects_app/wms/cell_detail.html", {
        "site": site,
        "site_code": site.code.lower(),
        "cell": cell,
        "occupancy": active_occupancy,
        "history": history,
        **get_wms_menu_context(request, site),
    })

@login_required
@wms_site_permission_required("map_edit")
@require_POST
def wms_toggle_cell_active_view(request, site_code, cell_id):
    site = get_wms_site_or_404(site_code)

    cell = get_object_or_404(
        WmsStorageCell.objects.select_related("line", "line__warehouse", "line__warehouse__site"),
        id=cell_id,
        line__warehouse__site=site,
    )

    has_active_placements = WmsPalletPlacement.objects.filter(
        cell=cell,
        is_active=True,
    ).exists()

    if cell.is_active and has_active_placements:
        messages.error(request, "Нельзя отключить ячейку: в ней есть активные размещения.")
        return redirect(
            "wms_cell_detail",
            site_code=site.code.lower(),
            cell_id=cell.id,
        )

    cell.is_active = not cell.is_active
    cell.save(update_fields=["is_active"])

    if cell.is_active:
        messages.success(request, f"Ячейка {cell.address} снова доступна.")
    else:
        messages.success(request, f"Ячейка {cell.address} отключена и не будет предлагаться для размещения.")

    return redirect(
        "wms_cell_detail",
        site_code=site.code.lower(),
        cell_id=cell.id,
    )

@login_required
@wms_site_permission_required("cancel")
@require_POST
def wms_remove_placement_view(request, site_code, placement_id):
    site = get_wms_site_or_404(site_code)

    placement = get_object_or_404(
        WmsPalletPlacement.objects.select_related(
            "cell",
            "cell__line",
            "cell__line__warehouse",
            "cell__line__warehouse__site",
        ),
        id=placement_id,
        cell__line__warehouse__site=site,
    )

    cell_id = placement.cell_id

    remove_pallet(placement, request.user)

    messages.success(request, "Поддон снят с ячейки. История сохранена.")

    return redirect(
        "wms_cell_detail",
        site_code=site.code.lower(),
        cell_id=cell_id,
    )

def generate_code128_svg(value):
    buffer = BytesIO()

    code128 = barcode.get(
        "code128",
        str(value),
        writer=SVGWriter()
    )

    code128.write(buffer, {
        "module_width": 0.35,
        "module_height": 14,
        "font_size": 0,
        "text_distance": 0,
        "quiet_zone": 1.5,
        "write_text": False,
    })

    return buffer.getvalue().decode("utf-8")

@login_required
@wms_site_permission_required("view")
def wms_container_labels_view(request, site_code, container_id):
    site = get_wms_site_or_404(site_code)

    container = get_object_or_404(
        WmsContainer.objects.select_related("lot", "lot__site"),
        id=container_id,
        lot__site=site,
    )

    label_size = request.GET.get("size", "75x120")

    orientation = request.GET.get("orientation", "landscape")

    if orientation not in ["portrait", "landscape"]:
        orientation = "landscape"

    if label_size not in ["58x40", "75x120"]:
        label_size = "75x120"

    cases = WmsCase.objects.filter(
        container=container,
        is_active=True,
    ).prefetch_related("boxes").order_by("case_number")

    for case in cases:
        case.barcode_svg = generate_code128_svg(case.case_number)

    return render(request, "defects_app/wms/container_labels.html", {
        "site": site,
        "site_code": site.code.lower(),
        "container": container,
        "lot": container.lot,
        "cases": cases,
        "label_size": label_size,
        **get_wms_menu_context(request, site),
        "orientation": orientation,
    })