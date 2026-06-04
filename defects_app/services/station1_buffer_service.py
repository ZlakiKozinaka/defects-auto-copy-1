from django.db import IntegrityError, transaction
from django.utils import timezone

from defects_app.models import Avtomobili, StationOnePrintBufferEntry

STATION_ONE_BUFFER_BATCH_SIZE = 6
STATION_ONE_MAX_DAILY_NUMBER = 999


def build_station_one_sequence_number(for_date, daily_number):
    """Возвращает sequence станции 1 в формате DDMMYYYYNNN."""
    return f"{for_date:%d%m%Y}{daily_number:03d}"


def get_station_one_buffer_count():
    return StationOnePrintBufferEntry.objects.filter(printed_at__isnull=True).count()


def assign_station_one_sequence_number(car):
    """
    Присваивает машине ежедневный sequence станции 1.

    Номер формируется как DDMMYYYYNNN, где NNN — порядковый номер создания
    на станции 1 в рамках текущего дня. Если номер уже есть, он не меняется.
    """
    if car.station1_sequence_number:
        return car.station1_sequence_number

    today = timezone.now().date()
    prefix = f"{today:%d%m%Y}"

    for _ in range(3):
        try:
            with transaction.atomic():
                locked_car = Avtomobili.objects.select_for_update().get(pk=car.pk)
                if locked_car.station1_sequence_number:
                    car.station1_sequence_number = locked_car.station1_sequence_number
                    return locked_car.station1_sequence_number

                last_car = (
                    Avtomobili.objects.select_for_update()
                    .filter(station1_sequence_number__startswith=prefix)
                    .order_by("-station1_sequence_number")
                    .first()
                )
                if last_car and last_car.station1_sequence_number:
                    next_daily_number = int(last_car.station1_sequence_number[-3:]) + 1
                else:
                    next_daily_number = 1

                if next_daily_number > STATION_ONE_MAX_DAILY_NUMBER:
                    raise IntegrityError("Дневной лимит sequence номеров станции 1 исчерпан.")

                locked_car.station1_sequence_number = build_station_one_sequence_number(today, next_daily_number)
                locked_car.save(update_fields=["station1_sequence_number"])
                car.station1_sequence_number = locked_car.station1_sequence_number
                return locked_car.station1_sequence_number
        except IntegrityError:
            # На случай одновременного создания двух машин: уникальный индекс
            # не даст записать дубль, после чего пробуем взять следующий номер.
            continue

    raise IntegrityError("Не удалось присвоить sequence номер станции 1.")


def add_car_to_station_one_buffer(car):
    """
    Добавляет машину в общий DB-буфер станции 1.

    Возвращает список из 6 id машин для печати, когда буфер набран, иначе None.
    Уже отправленные в 6-листник машины повторно в активный буфер не возвращаются.
    """
    with transaction.atomic():
        StationOnePrintBufferEntry.objects.get_or_create(car=car)

        active_entries = list(
            StationOnePrintBufferEntry.objects.select_for_update()
            .filter(printed_at__isnull=True)
            .order_by("added_at", "id")[:STATION_ONE_BUFFER_BATCH_SIZE]
        )

        if len(active_entries) < STATION_ONE_BUFFER_BATCH_SIZE:
            return None

        now = timezone.now()
        entry_ids = [entry.id for entry in active_entries]
        StationOnePrintBufferEntry.objects.filter(id__in=entry_ids).update(printed_at=now)
        return [entry.car_id for entry in active_entries]