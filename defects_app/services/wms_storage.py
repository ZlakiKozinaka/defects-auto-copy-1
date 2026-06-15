from django.db import transaction
from django.utils import timezone

from defects_app.models import WmsOperation, WmsPalletPlacement

from defects_app.models import WmsStorageCell, WmsStorageLine

class WmsStorageError(ValueError):
    pass

def create_wms_operation(
    operation_type,
    user=None,
    lot=None,
    container=None,
    case=None,
    pallet=None,
    placement=None,
    cell=None,
    message="",
    data=None,
):
    return WmsOperation.objects.create(
        operation_type=operation_type,
        lot=lot,
        container=container,
        case=case,
        pallet=pallet,
        placement=placement,
        cell=cell,
        message=message,
        data=data or {},
        performed_by=getattr(user, "username", str(user)) if user else "",
    )

def get_active_placements(cell):
    return WmsPalletPlacement.objects.filter(
        cell=cell,
        is_active=True,
    ).select_related(
        "pallet",
        "pallet__pallet_type",
        "pallet__storage_unit",
        "pallet__storage_unit__container",
        "pallet__storage_unit__container__lot",
        "pallet__storage_unit__case",
        "pallet__storage_unit__box",
        "cell",
        "cell__line",
    ).order_by("position_from")


def get_cell_occupancy(cell):
    placements = list(get_active_placements(cell))
    occupied_units = set()

    for placement in placements:
        occupied_units.update(range(placement.position_from, placement.position_to + 1))

    occupied_count = len(occupied_units)
    if occupied_count == 0:
        status = "free"
        status_label = "Свободно"
    elif occupied_count >= cell.capacity_units:
        status = "full"
        status_label = "Полностью занято"
    else:
        status = "partial"
        status_label = "Частично занято"

    return {
        "cell": cell,
        "placements": placements,
        "units": list(range(1, cell.capacity_units + 1)),
        "occupied_units": sorted(occupied_units),
        "occupied_count": occupied_count,
        "free_units": max(cell.capacity_units - occupied_count, 0),
        "capacity_units": cell.capacity_units,
        "status": status,
        "status_label": status_label,
    }


def range_is_free(cell, position_from, position_to):
    return not WmsPalletPlacement.objects.filter(
        cell=cell,
        is_active=True,
        position_from__lte=position_to,
        position_to__gte=position_from,
    ).exists()


def get_free_ranges(cell):
    occupied_units = set(get_cell_occupancy(cell)["occupied_units"])
    ranges = []
    start = None

    for unit in range(1, cell.capacity_units + 1):
        if unit not in occupied_units and start is None:
            start = unit
        if (unit in occupied_units or unit == cell.capacity_units) and start is not None:
            end = unit - 1 if unit in occupied_units else unit
            ranges.append((start, end))
            start = None

    return ranges


def get_position_label(position_from, position_to, capacity_units):
    width = position_to - position_from + 1

    if position_from == 1:
        return "Слева"

    if position_to == capacity_units:
        return "Справа"

    center_start = (capacity_units - width) // 2 + 1
    center_to = center_start + width - 1

    if position_from == center_start and position_to == center_to:
        return "По центру"

    return f"Позиция {position_from}-{position_to}"


def get_position_choices_for_pallet_type(cell, pallet_type):
    choices = []

    if cell is None:
        capacity_units = 6
        occupied_ranges_check = False
    else:
        capacity_units = cell.capacity_units
        occupied_ranges_check = True

    width_units = pallet_type.width_units

    if width_units <= 0:
        return [("", "Некорректная ширина типа поддона")]

    if width_units > capacity_units:
        return [("", f"{pallet_type.name} не помещается в ячейку")]

    for position_from in range(1, capacity_units + 1, width_units):
        position_to = position_from + width_units - 1

        if position_to > capacity_units:
            continue

        if occupied_ranges_check:
            allowed, _ = can_place_pallet(cell, pallet_type, position_from, position_to)
            if not allowed:
                continue

        label = get_position_label(position_from, position_to, capacity_units)
        choices.append((
            f"{position_from}-{position_to}",
            f"{label} [{position_from}-{position_to}]",
        ))

    if not choices:
        choices.append(("", "Нет доступных позиций"))

    return choices


def can_place_pallet(cell, pallet_type, position_from, position_to, pallet=None):
    width = position_to - position_from + 1

    if not cell.is_active:
        return False, "Ячейка отключена."

    if not cell.line.is_active:
        return False, "Ряд склада отключён."

    if not cell.line.warehouse.is_active:
        return False, "Склад отключён."

    if hasattr(cell.line.warehouse, "site") and not cell.line.warehouse.site.is_active:
        return False, "Площадка склада отключена."

    if position_from < 1 or position_to < position_from:
        return False, "Некорректный диапазон позиции."

    if position_to > cell.capacity_units:
        return False, "Позиция выходит за вместимость ячейки."

    if width != pallet_type.width_units:
        return False, f"Для типа поддона {pallet_type.name} нужно {pallet_type.width_units} условных единиц подряд."

    if pallet and WmsPalletPlacement.objects.filter(pallet=pallet, is_active=True).exists():
        return False, "У поддона уже есть активное размещение."

    if not range_is_free(cell, position_from, position_to):
        return False, "Выбранная позиция пересекается с уже занятым местом."

    return True, ""


@transaction.atomic
def place_pallet(pallet, cell, position_from, position_to, user):
    cell = cell.__class__.objects.select_for_update().select_related(
        "line",
        "line__warehouse",
        "line__warehouse__site",
    ).get(pk=cell.pk)
    pallet = pallet.__class__.objects.select_for_update().select_related("pallet_type").get(pk=pallet.pk)

    allowed, message = can_place_pallet(cell, pallet.pallet_type, position_from, position_to, pallet=pallet)
    if not allowed:
        raise WmsStorageError(message)

    placement = WmsPalletPlacement.objects.create(
        pallet=pallet,
        cell=cell,
        position_from=position_from,
        position_to=position_to,
        placed_by=getattr(user, "username", str(user)) if user else "",
    )

    storage_unit = pallet.storage_unit
    create_wms_operation(
        WmsOperation.OP_PLACE,
        user=user,
        lot=storage_unit.lot,
        container=storage_unit.container or (storage_unit.case.container if storage_unit.case_id else None),
        case=storage_unit.case,
        pallet=pallet,
        placement=placement,
        cell=cell,
        message=f"Размещение {storage_unit.display_name} в {cell.address} [{position_from}-{position_to}]",
        data={
            "position_from": position_from,
            "position_to": position_to,
            "pallet_type": pallet.pallet_type.code,
        },
    )

    return placement


@transaction.atomic
def remove_pallet(placement, user):
    placement = WmsPalletPlacement.objects.select_for_update().get(pk=placement.pk)
    if not placement.is_active:
        return placement

    placement.is_active = False
    placement.removed_at = timezone.now()
    placement.removed_by = getattr(user, "username", str(user)) if user else ""
    placement.save(update_fields=["is_active", "removed_at", "removed_by"])
    storage_unit = placement.pallet.storage_unit
    create_wms_operation(
        WmsOperation.OP_REMOVE,
        user=user,
        lot=storage_unit.lot,
        container=storage_unit.container or (storage_unit.case.container if storage_unit.case_id else None),
        case=storage_unit.case,
        pallet=placement.pallet,
        placement=placement,
        cell=placement.cell,
        message=f"Снятие {storage_unit.display_name} с {placement.cell.address}",
        data={
            "position_from": placement.position_from,
            "position_to": placement.position_to,
        },
    )
    return placement


@transaction.atomic
def move_pallet(pallet, new_cell, position_from, position_to, user):
    pallet = pallet.__class__.objects.select_for_update().select_related(
        "pallet_type",
        "storage_unit",
    ).get(pk=pallet.pk)

    new_cell = new_cell.__class__.objects.select_for_update().select_related(
        "line",
        "line__warehouse",
        "line__warehouse__site",
    ).get(pk=new_cell.pk)

    active_placement = WmsPalletPlacement.objects.select_for_update().filter(
        pallet=pallet,
        is_active=True,
    ).first()

    # Временно не учитываем старое размещение этого же поддона при проверке нового места.
    if active_placement:
        active_placement.is_active = False
        active_placement.save(update_fields=["is_active"])

    allowed, message = can_place_pallet(
        new_cell,
        pallet.pallet_type,
        position_from,
        position_to,
        pallet=None,
    )

    if not allowed:
        if active_placement:
            active_placement.is_active = True
            active_placement.save(update_fields=["is_active"])
        raise WmsStorageError(message)

    if active_placement:
        active_placement.is_active = True
        active_placement.save(update_fields=["is_active"])
        remove_pallet(active_placement, user)

    return place_pallet(pallet, new_cell, position_from, position_to, user)

def suggest_best_places_for_pallet_type(
    pallet_type,
    base_line_code="A",
    base_column=1,
    base_level=1,
    limit=3,
    site=None,
):
    base_line_query = WmsStorageLine.objects.filter(
        code=base_line_code,
        is_active=True,
        warehouse__is_active=True,
        warehouse__site__is_active=True,
    )

    if site is not None:
        base_line_query = base_line_query.filter(warehouse__site=site)

    base_line = base_line_query.order_by("warehouse__code", "sort_order").first()

    base_sort_order = base_line.sort_order if base_line else 0

    cells_query = WmsStorageCell.objects.filter(
        is_active=True,
        line__is_active=True,
        line__warehouse__is_active=True,
        line__warehouse__site__is_active=True,
    )

    if site is not None:
        cells_query = cells_query.filter(line__warehouse__site=site)

    cells = list(
        cells_query
        .select_related("line", "line__warehouse", "line__warehouse__site")
        .order_by("line__sort_order", "column_number", "level_number")
    )

    cell_ids = [cell.id for cell in cells]

    active_placements = WmsPalletPlacement.objects.filter(
        cell_id__in=cell_ids,
        is_active=True,
    ).select_related("cell")

    occupied_by_cell = {}

    for placement in active_placements:
        occupied_by_cell.setdefault(placement.cell_id, set()).update(
            range(placement.position_from, placement.position_to + 1)
        )

    suggestions = []

    for cell in cells:
        if pallet_type.width_units > cell.capacity_units:
            continue

        occupied_units = occupied_by_cell.get(cell.id, set())
        occupied_count = len(occupied_units)
        free_units = cell.capacity_units - occupied_count

        if free_units < pallet_type.width_units:
            continue

        for position_from in range(1, cell.capacity_units + 1, pallet_type.width_units):
            position_to = position_from + pallet_type.width_units - 1

            if position_to > cell.capacity_units:
                continue
            candidate_units = set(range(position_from, position_to + 1))

            if occupied_units.intersection(candidate_units):
                continue

            free_after = free_units - pallet_type.width_units

            line_distance = abs((cell.line.sort_order or 0) - base_sort_order)
            column_distance = abs(cell.column_number - base_column)

            level_distance = abs(cell.level_number - base_level)

            score = (
                line_distance,
                column_distance,
                level_distance,
                free_after,
                position_from,
            )

            suggestions.append({
                "cell": cell,
                "position_from": position_from,
                "position_to": position_to,
                "position_label": get_position_label(position_from, position_to, cell.capacity_units),
                "occupied_count": occupied_count,
                "capacity_units": cell.capacity_units,
                "free_after": free_after,
                "score": score,
            })

    suggestions.sort(key=lambda item: item["score"])

    return suggestions[:limit]