from decimal import Decimal, InvalidOperation

from django.db import transaction

from defects_app.models import (
    WmsBox,
    WmsBoxItem,
    WmsCase,
    WmsContainer,
    WmsLot,
    WmsOperation,
    WmsPalletPlacement,
    WmsStorageUnit,
)
from defects_app.services.wms_storage import create_wms_operation, remove_pallet


class WmsIssueError(ValueError):
    pass


def parse_issue_quantity(value):
    try:
        quantity = Decimal(str(value).replace(",", ".").strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise WmsIssueError("Введите корректное количество.")

    if quantity <= 0:
        raise WmsIssueError("Количество должно быть больше 0.")

    return quantity


@transaction.atomic
def issue_box_item(item_id, quantity_to_take, user):
    quantity_to_take = parse_issue_quantity(quantity_to_take)

    item = WmsBoxItem.objects.select_for_update().select_related(
        "box",
        "box__case",
        "box__case__container",
        "box__case__container__lot",
    ).get(id=item_id)

    if not item.is_active:
        raise WmsIssueError("Эта позиция уже закрыта.")

    if quantity_to_take > item.quantity:
        raise WmsIssueError(
            f"Нельзя забрать {quantity_to_take}. Остаток: {item.quantity}."
        )

    old_quantity = item.quantity
    item.quantity = item.quantity - quantity_to_take

    box = item.box
    case = box.case
    container = case.container
    lot = container.lot

    create_wms_operation(
        WmsOperation.OP_PICK,
        user=user,
        lot=lot,
        container=container,
        case=case,
        cell=_get_case_active_cell(case),
        message=(
            f"Выдача {quantity_to_take} шт. парт-номера {item.part_number} "
            f"из коробки {box.box_number}, кейс {case.case_number}"
        ),
        data={
            "box_item_id": item.id,
            "box_number": box.box_number,
            "case_number": case.case_number,
            "container_number": container.container_number,
            "part_number": item.part_number,
            "old_quantity": str(old_quantity),
            "taken_quantity": str(quantity_to_take),
            "new_quantity": str(item.quantity),
        },
    )

    messages = [
        f"Забрано {quantity_to_take} шт. {item.part_number}. Остаток: {item.quantity}."
    ]

    if item.quantity == 0:
        item.is_active = False
        item.save(update_fields=["quantity", "is_active"])

        create_wms_operation(
            WmsOperation.OP_CLOSE_ITEM,
            user=user,
            lot=lot,
            container=container,
            case=case,
            cell=_get_case_active_cell(case),
            message=f"Позиция {item.part_number} закрыта, остаток 0.",
            data={"box_item_id": item.id, "part_number": item.part_number},
        )
        messages.append(f"Позиция {item.part_number} закрыта.")
    else:
        item.save(update_fields=["quantity"])

    if not WmsBoxItem.objects.filter(box=box, is_active=True).exists():
        box.is_active = False
        box.save(update_fields=["is_active"])

        create_wms_operation(
            WmsOperation.OP_CLOSE_BOX,
            user=user,
            lot=lot,
            container=container,
            case=case,
            cell=_get_case_active_cell(case),
            message=f"Коробка {box.box_number} закрыта: активных парт-номеров нет.",
            data={"box_id": box.id, "box_number": box.box_number},
        )
        messages.append(f"Коробка {box.box_number} закрыта.")

    if not WmsBox.objects.filter(case=case, is_active=True).exists():
        _close_case_and_free_place(case, user, messages)

    if not WmsCase.objects.filter(container=container, is_active=True).exists():
        container.is_active = False
        container.save(update_fields=["is_active"])

        create_wms_operation(
            WmsOperation.OP_CLOSE_CONTAINER,
            user=user,
            lot=lot,
            container=container,
            message=f"Контейнер {container.container_number} закрыт: активных кейсов нет.",
            data={"container_id": container.id, "container_number": container.container_number},
        )
        messages.append(f"Контейнер {container.container_number} закрыт.")

    if not WmsContainer.objects.filter(lot=lot, is_active=True).exists():
        lot.is_active = False
        lot.save(update_fields=["is_active"])

        create_wms_operation(
            WmsOperation.OP_CLOSE_LOT,
            user=user,
            lot=lot,
            message=f"Лот {lot.lot_number} закрыт: активных контейнеров нет.",
            data={"lot_id": lot.id, "lot_number": lot.lot_number},
        )
        messages.append(f"Лот {lot.lot_number} закрыт.")

    return messages


def _get_case_active_cell(case):
    placement = WmsPalletPlacement.objects.filter(
        pallet__storage_unit__case=case,
        is_active=True,
    ).select_related("cell").first()

    return placement.cell if placement else None


def _close_case_and_free_place(case, user, messages):
    container = case.container
    lot = container.lot

    case.is_active = False
    case.save(update_fields=["is_active"])

    WmsStorageUnit.objects.filter(
        unit_type=WmsStorageUnit.UNIT_CASE,
        case=case,
    ).update(is_active=False)

    active_placements = WmsPalletPlacement.objects.filter(
        pallet__storage_unit__case=case,
        is_active=True,
    ).select_related("pallet", "cell")

    freed_addresses = []

    for placement in active_placements:
        freed_addresses.append(placement.cell.address)
        remove_pallet(placement, user)

    create_wms_operation(
        WmsOperation.OP_CLOSE_CASE,
        user=user,
        lot=lot,
        container=container,
        case=case,
        message=f"Кейс {case.case_number} закрыт: активных коробок нет.",
        data={
            "case_id": case.id,
            "case_number": case.case_number,
            "freed_addresses": freed_addresses,
        },
    )

    if freed_addresses:
        messages.append(
            f"Кейс {case.case_number} закрыт, ячейка освобождена: {', '.join(freed_addresses)}."
        )
    else:
        messages.append(f"Кейс {case.case_number} закрыт.")