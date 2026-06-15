import os
from django.conf import settings
from django.db import models
from django.utils import timezone


class Modeli(models.Model):
    nazvanie = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Модель"
        verbose_name_plural = "Модели"

    def __str__(self):
        return self.nazvanie


class Smeny(models.Model):
    nazvanie = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Смена"
        verbose_name_plural = "Смены"

    def __str__(self):
        return self.nazvanie


class Mesta(models.Model):
    nazvanie = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.nazvanie


class Tipy(models.Model):
    nazvanie = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тип"
        verbose_name_plural = "Типы"

    def __str__(self):
        return self.nazvanie


class Oblasti(models.Model):
    nazvanie = models.CharField(max_length=150, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Области"

    def __str__(self):
        return self.nazvanie


class Greydy(models.Model):
    nazvanie = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Грейд"
        verbose_name_plural = "Грейды"

    def __str__(self):
        return self.nazvanie


class Otvetstvennye(models.Model):
    nazvanie = models.CharField(max_length=150, unique=True, verbose_name="Название")
    aktiven = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Ответственный"
        verbose_name_plural = "Ответственные"

    def __str__(self):
        return self.nazvanie


class Stancii(models.Model):
    nazvanie = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Станция"
        verbose_name_plural = "Станции"

    def __str__(self):
        return self.nazvanie


class Avtomobili(models.Model):
    vin = models.CharField(max_length=17, unique=True, verbose_name="VIN")
    model = models.ForeignKey(Modeli, on_delete=models.PROTECT, verbose_name="Модель")
    data_sozdaniya = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    created_on_station_1 = models.BooleanField(default=True, verbose_name="Создана на станции 1")
    station1_sequence_number = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name="Sequence номер станции 1")
    kto_sozdal = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто создал машину")
    proshla_bestenevaya = models.BooleanField(default=False, verbose_name="Прошла Бестеневую")
    data_prohoda_bestenevaya = models.DateTimeField(blank=True, null=True, verbose_name="Дата прохода Бестеневой")
    telematika = models.CharField(max_length=150, blank=True, null=True, verbose_name="Телематика")
    privyazal_telematiku = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал телематику")
    data_privyazki_telematiki = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки телематики")
    glonass = models.CharField(max_length=150, blank=True, null=True, verbose_name="Глонасс")
    glonass_kto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал глонасс")
    glonass_kogda = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки глонасса")
    glonass_sn = models.CharField(max_length=50, blank=True, null=True, verbose_name="Серийный номер")
    glonass_imei = models.CharField(max_length=50, blank=True, null=True, verbose_name="IMEI Глонасс")
    glonass_iccid = models.CharField(max_length=50, blank=True, null=True, verbose_name="ICCID Глонасс")
    dvs = models.CharField(max_length=100, blank=True, null=True, verbose_name="ДВС")
    dvs_kto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал ДВС")
    dvs_kogda = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки ДВС")
    batareya = models.CharField(max_length=150, blank=True, null=True, verbose_name="Батарея")
    batareya_kto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал батарею")
    batareya_kogda = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки батареи")
    perednij_dvigatel = models.CharField(max_length=100, blank=True, null=True, verbose_name="Передний двигатель")
    perednij_dvigatel_kto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал передний двигатель")
    perednij_dvigatel_kogda = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки переднего двигателя")
    zadnij_dvigatel = models.CharField(max_length=100, blank=True, null=True, verbose_name="Задний двигатель")
    zadnij_dvigatel_kto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Привязал задний двигатель")
    zadnij_dvigatel_kogda = models.DateTimeField(blank=True, null=True, verbose_name="Дата привязки заднего двигателя")


    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return self.vin



class StationOnePrintBufferEntry(models.Model):
    car = models.OneToOneField(
        Avtomobili,
        on_delete=models.CASCADE,
        related_name="station1_print_buffer_entry",
        verbose_name="Автомобиль",
    )
    added_at = models.DateTimeField(default=timezone.now, verbose_name="Когда добавлена в буфер")
    printed_at = models.DateTimeField(blank=True, null=True, verbose_name="Когда отправлена в 6-листник")

    class Meta:
        verbose_name = "Запись буфера станции 1"
        verbose_name_plural = "Буфер станции 1"
        ordering = ["added_at", "id"]

    def __str__(self):
        return f"{self.car.vin} — {self.added_at:%d.%m.%Y %H:%M:%S}"

class Defekty(models.Model):
    avto = models.ForeignKey(Avtomobili, on_delete=models.CASCADE, verbose_name="Автомобиль")
    data = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    smena = models.ForeignKey(Smeny, on_delete=models.PROTECT, verbose_name="Смена")
    mesto = models.ForeignKey(Mesta, on_delete=models.PROTECT, verbose_name="Место")
    tip = models.ForeignKey(Tipy, on_delete=models.PROTECT, verbose_name="Тип")
    oblast = models.ForeignKey(Oblasti, on_delete=models.PROTECT, verbose_name="Область")
    greyd = models.ForeignKey(Greydy, on_delete=models.PROTECT, verbose_name="Грейд")
    otvetstvennyj = models.ForeignKey(Otvetstvennye, on_delete=models.SET_NULL, verbose_name="Ответственный", blank=True, null=True)
    stanciya = models.ForeignKey(Stancii, on_delete=models.PROTECT, verbose_name="Станция", blank=True, null=True)
    kommentarij = models.TextField(blank=True, null=True, verbose_name="Комментаррий")
    kto_sozdal = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто создал")
    ustraneno = models.BooleanField(default=False, verbose_name="Устранено")
    kto_ustranil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто устранил")
    data_ustraneniya = models.DateTimeField(blank=True, null=True, verbose_name="Дата устранения")
    proveren = models.BooleanField(default=False, verbose_name="Проверен")
    kto_razreshil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто разрешил")
    data_razresheniya = models.DateTimeField(blank=True, null=True, verbose_name="Дата разрешения")

    class Meta:
        verbose_name = "Дефект"
        verbose_name_plural = "Дефекты"

    def __str__(self):
        return f"Дефект {self.id} - {self.avto.vin}"


class SnpDefectComment(models.Model):
    defect = models.ForeignKey(
        "Defekty",
        on_delete=models.CASCADE,
        related_name="snp_comments",
        verbose_name="Дефект"
    )
    avto = models.ForeignKey(
        "Avtomobili",
        on_delete=models.CASCADE,
        related_name="snp_comments",
        verbose_name="Автомобиль"
    )
    comment = models.TextField(verbose_name="Комментарий причины отправки на СНП")
    kto_sozdal = models.CharField(max_length=150, verbose_name="Кто создал")
    data_sozdaniya = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    kto_izmenil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто изменил")
    data_izmeneniya = models.DateTimeField(blank=True, null=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "Комментарий СНП по дефекту"
        verbose_name_plural = "Комментарии СНП по дефектам"
        ordering = ["-data_sozdaniya"]

    def __str__(self):
        return f"{self.avto.vin} | Дефект {self.defect.id}"


class SnpDefectOrder(models.Model):
    defect = models.OneToOneField(
        Defekty,
        on_delete=models.CASCADE,
        related_name="snp_order",
        verbose_name="Дефект"
    )
    avto = models.ForeignKey(
        Avtomobili,
        on_delete=models.CASCADE,
        related_name="snp_orders",
        verbose_name="Автомобиль"
    )
    order_number = models.CharField(max_length=100, verbose_name="Номер заказа")
    kto_sozdal = models.CharField(max_length=150, verbose_name="Кто внёс")
    data_sozdaniya = models.DateTimeField(default=timezone.now, verbose_name="Дата внесения")
    kto_izmenil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто изменил")
    data_izmeneniya = models.DateTimeField(blank=True, null=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "Заказ СНП по дефекту"
        verbose_name_plural = "Заказы СНП по дефектам"

    def __str__(self):
        return f"{self.avto.vin} | Дефект {self.defect.id} | {self.order_number}"


class IstoriyaIzmeneniyAvto(models.Model):
    avto = models.ForeignKey(
        "Avtomobili",
        on_delete=models.CASCADE,
        related_name="istoriya_izmeneniy_avto",
        verbose_name="Автомобиль"
    )
    pole = models.CharField(max_length=100, verbose_name="Поле")
    staroe_znachenie = models.TextField(blank=True, null=True, verbose_name="Старое значение")
    novoe_znachenie = models.TextField(blank=True, null=True, verbose_name="Новое значение")
    kto_izmenil = models.CharField(max_length=150, verbose_name="Кто изменил")
    data_izmeneniya = models.DateTimeField(default=timezone.now, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "История изменения автомобиля"
        verbose_name_plural = "История изменений автомобилей"
        ordering = ["-data_izmeneniya"]

    def __str__(self):
        return f"{self.avto.vin} | {self.pole} | {self.data_izmeneniya}"


class IstoriyaIzmeneniyDefektov(models.Model):
    defekt = models.ForeignKey(
        "Defekty",
        on_delete=models.CASCADE,
        related_name="istoriya_izmeneniy_defektov",
        verbose_name="Дефект"
    )
    pole = models.CharField(max_length=100, verbose_name="Поле")
    staroe_znachenie = models.TextField(blank=True, null=True, verbose_name="Старое значение")
    novoe_znachenie = models.TextField(blank=True, null=True, verbose_name="Новое значение")
    kto_izmenil = models.CharField(max_length=150, verbose_name="Кто изменил")
    data_izmeneniya = models.DateTimeField(default=timezone.now, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "История изменения дефекта"
        verbose_name_plural = "История изменений дефектов"
        ordering = ["-data_izmeneniya"]

    def __str__(self):
        return f"Дефект {self.defekt.id} | {self.pole} | {self.data_izmeneniya}"

class StatusAvto(models.Model):
    avto = models.ForeignKey(Avtomobili, on_delete=models.CASCADE, verbose_name="Автомобиль")
    status = models.CharField(max_length=100, verbose_name="Статус")
    data_statusa = models.DateTimeField(default=timezone.now, verbose_name="Дата статуса")
    kto_izmenil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто изменил")

    class Meta:
        verbose_name = "Статус авто"
        verbose_name_plural = "Статусы авто"

    def __str__(self):
        return f"{self.avto.vin} - {self.status}"
    

class PlanovyeVin(models.Model):
    nomer_partii = models.CharField(max_length=50, verbose_name="№ партии")
    nomer_lota = models.CharField(max_length=100, verbose_name="№ лота")
    model = models.CharField(max_length=150, verbose_name="Модель")
    vin = models.CharField(max_length=17, unique=True, verbose_name="VIN рус")
    cvet_kuzova = models.CharField(max_length=100, verbose_name="Цвет кузова")
    cvet_salona = models.CharField(max_length=100, verbose_name="Цвет салона")
    komplektaciya = models.CharField(max_length=150, verbose_name="Комплектация")
    otts = models.CharField(max_length=100, verbose_name="ОТТС")

    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя файла")
    kto_zagruzil = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто загрузил")
    data_zagruzki = models.DateTimeField(default=timezone.now, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Плановый VIN"
        verbose_name_plural = "Плановые VIN"
        ordering = ["id"]

    def __str__(self):
        return self.vin

class DailyProductionPlan(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата")

    plan_count = models.PositiveIntegerField(
        verbose_name="План машин за смену"
    )

    work_minutes = models.PositiveIntegerField(default=450, verbose_name="Рабочие минуты")

    created_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Кто создал"
    )

    updated_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Кто изменил"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения"
    )

    class Meta:
        verbose_name = "План выпуска"
        verbose_name_plural = "Планы выпуска"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.plan_count}"
    
class DefectApprovalForSgp(models.Model):
    defect = models.OneToOneField(
        "Defekty",
        on_delete=models.CASCADE,
        related_name="sgp_approval",
        verbose_name="Согласованный дефект"
    )

    avto = models.ForeignKey(
        "Avtomobili",
        on_delete=models.CASCADE,
        related_name="sgp_defect_approvals",
        verbose_name="Автомобиль"
    )

    approved_by = models.CharField(
        max_length=150,
        verbose_name="Кто согласовал"
    )

    approved_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата согласования"
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий согласования"
    )

    class Meta:
        verbose_name = "Согласование дефекта для СГП"
        verbose_name_plural = "Согласования дефектов для СГП"
        ordering = ["-approved_at"]

    def __str__(self):
        return f"{self.avto.vin} | Дефект {self.defect.id} | {self.approved_by}"
    

class VinPrefix(models.Model):
    model = models.ForeignKey(
        Modeli,
        on_delete=models.CASCADE,
        related_name="vin_prefixes",
        verbose_name="Модель"
    )

    prefix = models.CharField(
        max_length=17,
        verbose_name="Начало VIN"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен для автоподстановки"
    )

    comment = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )

    show_in_select = models.BooleanField(
        default=True,
        verbose_name="Показывать в списке"
    )

    class Meta:
        verbose_name = "Префикс VIN"
        verbose_name_plural = "Префиксы VIN"        
        ordering = ["model__nazvanie", "prefix"]

    def __str__(self):
        return f"{self.model} — {self.prefix}"
    

class DefectPhoto(models.Model):
    defect = models.ForeignKey(
        "Defekty",
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Дефект"
    )

    avto = models.ForeignKey(
        "Avtomobili",
        on_delete=models.CASCADE,
        related_name="defect_photos",
        verbose_name="Автомобиль",
        blank=True,
        null=True,
    )

    image = models.ImageField(
        upload_to="defects_photos/%Y/%m/%d/",
        verbose_name="Фото дефекта"
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Исходное имя файла"
    )

    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Размер файла, байт"
    )

    uploaded_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Кто загрузил"
    )

    uploaded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата загрузки"
    )

    class Meta:
        verbose_name = "Фото дефекта"
        verbose_name_plural = "Фото дефектов"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Фото дефекта {self.defect.id}"
    
class Container(models.Model):
    number = models.CharField(max_length=50, verbose_name="Номер контейнера")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.number


class ContainerReceipt(models.Model):
    daily_number = models.PositiveIntegerField(verbose_name="Номер акта за день")
    receipt_date = models.DateField(verbose_name="Дата поступления")
    vehicle_number = models.CharField(max_length=20, verbose_name="Номер машины")
    submission_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    container = models.ForeignKey(Container, on_delete=models.PROTECT, related_name="receipts")
    components_name = models.CharField(max_length=255, verbose_name="Наименование комплектующих изделий", blank=True)
    batch_number = models.CharField(max_length=100, verbose_name="Номер партии", blank=True)
    package_number = models.CharField(max_length=100, verbose_name="Номер упаковки", blank=True)
    package_marking = models.CharField(max_length=255, verbose_name="Маркировка упаковочной тары", blank=True)
    created_by = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Акт №{self.daily_number} от {self.receipt_date} — {self.container}"


class ContainerSeal(models.Model):
    receipt = models.ForeignKey(ContainerReceipt, on_delete=models.CASCADE, related_name="seals")
    seal_number = models.CharField(max_length=100, verbose_name="Номер пломбы")

    def __str__(self):
        return self.seal_number


class ContainerReceiptPhoto(models.Model):
    receipt = models.ForeignKey(ContainerReceipt, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="container_receipts/%Y/%m/%d/")
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_by = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

class ContainerCar(models.Model):
    receipt = models.ForeignKey(
        ContainerReceipt,
        on_delete=models.CASCADE,
        related_name="cars",
    )

    avto = models.ForeignKey(
        Avtomobili,
        on_delete=models.CASCADE,
        related_name="container_receipts",
    )

    accepted_by = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    accepted_at = models.DateTimeField(
        auto_now_add=True,
    )

    comment = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["receipt", "avto"],
                name="unique_container_car_per_receipt",
            ),
        ]
    
    def __str__(self):
        return f"{self.avto.vin} -> {self.receipt.container.number}"
    

class ContainerCarPhoto(models.Model):
    container_car = models.ForeignKey(
        ContainerCar,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to="container_car_photos/%Y/%m/%d/",
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    uploaded_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    uploaded_at = models.DateTimeField(
        default=timezone.now,
    )

    def __str__(self):
        return f"Фото приемки кузова {self.container_car.avto.vin}"

class WmsLot(models.Model):
    site = models.ForeignKey(
        "WmsSite",
        on_delete=models.PROTECT,
        related_name="lots",
        blank=True,
        null=True,
        verbose_name="Площадка",
    )

    lot_number = models.CharField(max_length=100, verbose_name="Номер лота")
    display_name = models.CharField(max_length=255, blank=True, verbose_name="Название")
    source_file = models.FileField(upload_to="wms/lots/%Y/%m/%d/", blank=True, null=True, verbose_name="Исходный Excel-файл")
    uploaded_by = models.CharField(max_length=150, blank=True, verbose_name="Кто загрузил")
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name="Дата загрузки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "WMS лот"
        verbose_name_plural = "WMS лоты"
        ordering = ["-uploaded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "lot_number"],
                name="unique_wms_lot_per_site",
            ),
        ]
        permissions = [
            ("wms_view", "Can view WMS"),
            ("wms_import_lot", "Can import WMS lots"),
            ("wms_place", "Can place WMS pallets"),
            ("wms_move", "Can move WMS pallets"),
            ("wms_admin", "Can administrate WMS"),
        ]

    def __str__(self):
        return self.lot_number


class WmsContainer(models.Model):
    lot = models.ForeignKey(WmsLot, on_delete=models.CASCADE, related_name="containers", verbose_name="Лот")
    container_number = models.CharField(max_length=100, verbose_name="Номер контейнера")
    seal_number = models.CharField(max_length=100, blank=True, verbose_name="Номер пломбы")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    existing_container = models.ForeignKey(
        "Container",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wms_containers",
        verbose_name="Связанный контейнер приемки",
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "WMS контейнер"
        verbose_name_plural = "WMS контейнеры"
        ordering = ["container_number"]
        constraints = [
            models.UniqueConstraint(fields=["lot", "container_number"], name="unique_wms_container_per_lot"),
        ]

    def __str__(self):
        return f"{self.lot.lot_number} / {self.container_number}"


class WmsCase(models.Model):
    container = models.ForeignKey(WmsContainer, on_delete=models.CASCADE, related_name="cases", verbose_name="Контейнер")
    case_number = models.CharField(max_length=100, verbose_name="Номер кейса")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "WMS кейс"
        verbose_name_plural = "WMS кейсы"
        ordering = ["case_number"]
        constraints = [
            models.UniqueConstraint(fields=["container", "case_number"], name="unique_wms_case_per_container"),
        ]

    def __str__(self):
        return f"{self.container.container_number} / {self.case_number}"


class WmsBox(models.Model):
    case = models.ForeignKey(WmsCase, on_delete=models.CASCADE, related_name="boxes", verbose_name="Кейс")
    box_number = models.CharField(max_length=100, verbose_name="Номер коробки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "WMS коробка"
        verbose_name_plural = "WMS коробки"
        ordering = ["box_number"]
        constraints = [
            models.UniqueConstraint(fields=["case", "box_number"], name="unique_wms_box_per_case"),
        ]

    def __str__(self):
        return f"{self.case.case_number} / {self.box_number}"


class WmsBoxItem(models.Model):
    box = models.ForeignKey(WmsBox, on_delete=models.CASCADE, related_name="items", verbose_name="Коробка")
    part_number = models.CharField(max_length=150, verbose_name="SAP Part Number")
    row_number = models.PositiveIntegerField(default=0, verbose_name="Номер строки Excel")
    chinese_name = models.CharField(max_length=255, blank=True, verbose_name="Китайское наименование")
    chinese_description = models.TextField(blank=True, verbose_name="Китайское описание")
    english_name = models.CharField(max_length=255, blank=True, verbose_name="Английское наименование")
    english_description = models.TextField(blank=True, verbose_name="Английское описание")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Количество")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Ед. изм.")
    gross_weight = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True, verbose_name="Вес брутто")
    net_weight = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True, verbose_name="Вес нетто")
    volume = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True, verbose_name="Объем")
    raw_data = models.JSONField(default=dict, blank=True, verbose_name="Исходная строка Excel")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "WMS позиция коробки"
        verbose_name_plural = "WMS позиции коробок"
        ordering = ["part_number", "id"]
        constraints = [
            models.UniqueConstraint(fields=["box", "part_number", "row_number"], name="unique_wms_item_part_row_per_box"),
        ]

    def __str__(self):
        return f"{self.part_number} — {self.quantity}"

class WmsSite(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Код площадки")
    name = models.CharField(max_length=150, verbose_name="Название площадки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "WMS площадка"
        verbose_name_plural = "WMS площадки"
        ordering = ["code"]

    def __str__(self):
        return self.name

class WmsWarehouse(models.Model):
    site = models.ForeignKey(
        WmsSite,
        on_delete=models.PROTECT,
        related_name="warehouses",
        verbose_name="Площадка",
    )
    name = models.CharField(max_length=150, verbose_name="Название склада")
    code = models.CharField(max_length=50, verbose_name="Код склада")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "WMS склад"
        verbose_name_plural = "WMS склады"
        ordering = ["site__code", "code"]
        constraints = [
            models.UniqueConstraint(fields=["site", "code"], name="unique_wms_warehouse_per_site"),
        ]

    def __str__(self):
        return self.name


class WmsStorageLine(models.Model):
    warehouse = models.ForeignKey(WmsWarehouse, on_delete=models.CASCADE, related_name="lines", verbose_name="Склад")
    code = models.CharField(max_length=10, verbose_name="Код ряда")
    name = models.CharField(max_length=150, blank=True, verbose_name="Название")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "WMS ряд склада"
        verbose_name_plural = "WMS ряды склада"
        ordering = ["warehouse__site__code", "warehouse__code", "sort_order", "code"]
        constraints = [
            models.UniqueConstraint(fields=["warehouse", "code"], name="unique_wms_line_per_warehouse"),
        ]

    def __str__(self):
        return f"{self.warehouse.code} / {self.code}"


class WmsStorageCell(models.Model):
    line = models.ForeignKey(WmsStorageLine, on_delete=models.CASCADE, related_name="cells", verbose_name="Ряд")
    column_number = models.PositiveIntegerField(verbose_name="Столбец")
    level_number = models.PositiveIntegerField(verbose_name="Этаж")
    capacity_units = models.PositiveIntegerField(default=6, verbose_name="Вместимость, условные единицы")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "WMS ячейка"
        verbose_name_plural = "WMS ячейки"
        ordering = ["line__sort_order", "line__code", "column_number", "level_number"]
        constraints = [
            models.UniqueConstraint(fields=["line", "column_number", "level_number"], name="unique_wms_cell_per_line_column_level"),
        ]

    @property
    def address(self):
        return f"{self.line.code}{self.column_number};{self.level_number}"

    def __str__(self):
        return self.address


class WmsPalletType(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    width_units = models.PositiveIntegerField(verbose_name="Ширина, условные единицы")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "WMS тип поддона"
        verbose_name_plural = "WMS типы поддонов"
        ordering = ["code"]

    def __str__(self):
        return self.name

class WmsStorageUnit(models.Model):
    UNIT_CONTAINER = "CONTAINER"
    UNIT_CASE = "CASE"
    UNIT_BOX = "BOX"

    UNIT_TYPE_CHOICES = [
        (UNIT_CONTAINER, "Контейнер"),
        (UNIT_CASE, "Кейс"),
        (UNIT_BOX, "Коробка"),
    ]

    unit_type = models.CharField(
        max_length=30,
        choices=UNIT_TYPE_CHOICES,
        verbose_name="Тип складской единицы",
    )

    container = models.ForeignKey(
        WmsContainer,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="storage_units",
        verbose_name="Контейнер",
    )

    case = models.ForeignKey(
        WmsCase,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="storage_units",
        verbose_name="Кейс",
    )

    box = models.ForeignKey(
        WmsBox,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="storage_units",
        verbose_name="Коробка",
    )

    label = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Метка / номер складской единицы",
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    created_by = models.CharField(max_length=150, blank=True, verbose_name="Кто создал")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "WMS складская единица"
        verbose_name_plural = "WMS складские единицы"
        ordering = ["unit_type", "label", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit_type", "container"],
                condition=models.Q(container__isnull=False),
                name="unique_wms_storage_unit_container",
            ),
            models.UniqueConstraint(
                fields=["unit_type", "case"],
                condition=models.Q(case__isnull=False),
                name="unique_wms_storage_unit_case",
            ),
            models.UniqueConstraint(
                fields=["unit_type", "box"],
                condition=models.Q(box__isnull=False),
                name="unique_wms_storage_unit_box",
            ),
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(container__isnull=False) &
                        models.Q(case__isnull=True) &
                        models.Q(box__isnull=True)
                    )
                    |
                    (
                        models.Q(container__isnull=True) &
                        models.Q(case__isnull=False) &
                        models.Q(box__isnull=True)
                    )
                    |
                    (
                        models.Q(container__isnull=True) &
                        models.Q(case__isnull=True) &
                        models.Q(box__isnull=False)
                    )
                ),
                name="wms_storage_unit_exactly_one_object",
            ),
        ]

    def clean(self):
        filled = [self.container_id, self.case_id, self.box_id]
        filled_count = sum(1 for value in filled if value)

        if filled_count != 1:
            from django.core.exceptions import ValidationError
            raise ValidationError("Складская единица должна ссылаться ровно на один объект: контейнер, кейс или коробку.")

        if self.unit_type == self.UNIT_CONTAINER and not self.container_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("Для типа 'Контейнер' нужно выбрать контейнер.")

        if self.unit_type == self.UNIT_CASE and not self.case_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("Для типа 'Кейс' нужно выбрать кейс.")

        if self.unit_type == self.UNIT_BOX and not self.box_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("Для типа 'Коробка' нужно выбрать коробку.")

    @property
    def display_name(self):
        if self.container_id:
            return self.container.container_number
        if self.case_id:
            return self.case.case_number
        if self.box_id:
            return self.box.box_number
        return self.label or f"Складская единица #{self.id}"

    @property
    def lot(self):
        if self.container_id:
            return self.container.lot
        if self.case_id:
            return self.case.container.lot
        if self.box_id:
            return self.box.case.container.lot
        return None

    def __str__(self):
        return f"{self.get_unit_type_display()} — {self.display_name}"

class WmsPallet(models.Model):
    pallet_type = models.ForeignKey(WmsPalletType, on_delete=models.PROTECT, related_name="pallets", verbose_name="Тип поддона")
    pallet_number = models.CharField(max_length=100, blank=True, verbose_name="Номер поддона")
    storage_unit = models.ForeignKey(
        WmsStorageUnit,
        on_delete=models.PROTECT,
        related_name="pallets",
        verbose_name="Складская единица",
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    created_by = models.CharField(max_length=150, blank=True, verbose_name="Кто создал")

    class Meta:
        verbose_name = "WMS поддон"
        verbose_name_plural = "WMS поддоны"
        ordering = ["-created_at"]

    def __str__(self):
        number = self.pallet_number or f"#{self.id}"
        return f"{number} / {self.pallet_type.code}"


class WmsPalletPlacement(models.Model):
    pallet = models.ForeignKey(WmsPallet, on_delete=models.CASCADE, related_name="placements", verbose_name="Поддон")
    cell = models.ForeignKey(WmsStorageCell, on_delete=models.PROTECT, related_name="placements", verbose_name="Ячейка")
    position_from = models.PositiveIntegerField(verbose_name="Позиция с")
    position_to = models.PositiveIntegerField(verbose_name="Позиция по")
    placed_by = models.CharField(max_length=150, blank=True, verbose_name="Кто разместил")
    placed_at = models.DateTimeField(default=timezone.now, verbose_name="Когда разместил")
    removed_by = models.CharField(max_length=150, blank=True, null=True, verbose_name="Кто снял")
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name="Когда снял")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        verbose_name = "WMS размещение поддона"
        verbose_name_plural = "WMS размещения поддонов"
        ordering = ["-is_active", "cell__line__code", "cell__column_number", "cell__level_number", "position_from"]
        constraints = [
            models.CheckConstraint(condition=models.Q(position_from__gte=1), name="wms_placement_position_from_gte_1"),
            models.CheckConstraint(condition=models.Q(position_to__gte=1), name="wms_placement_position_to_gte_1"),
            models.CheckConstraint(condition=models.Q(position_to__gte=models.F("position_from")), name="wms_placement_position_to_gte_from"),
            models.UniqueConstraint(fields=["pallet"], condition=models.Q(is_active=True), name="unique_active_wms_placement_per_pallet"),
        ]

    @property
    def position_label(self):
        capacity_units = self.cell.capacity_units
        width = self.position_to - self.position_from + 1

        if self.position_from == 1:
            return "Слева"

        if self.position_to == capacity_units:
            return "Справа"

        center_start = (capacity_units - width) // 2 + 1
        center_to = center_start + width - 1

        if self.position_from == center_start and self.position_to == center_to:
            return "По центру"

        return f"Позиция {self.position_from}-{self.position_to}"

    def __str__(self):
        return f"{self.pallet} -> {self.cell.address} [{self.position_from}-{self.position_to}]"
    
class WmsOperation(models.Model):
    OP_IMPORT_LOT = "IMPORT_LOT"
    OP_PLACE = "PLACE"
    OP_REMOVE = "REMOVE"
    OP_MOVE = "MOVE"
    OP_REIMPORT_BLOCKED = "REIMPORT_BLOCKED"
    OP_PICK = "PICK"
    OP_CLOSE_ITEM = "CLOSE_ITEM"
    OP_CLOSE_BOX = "CLOSE_BOX"
    OP_CLOSE_CASE = "CLOSE_CASE"
    OP_CLOSE_CONTAINER = "CLOSE_CONTAINER"
    OP_CLOSE_LOT = "CLOSE_LOT"

    OPERATION_CHOICES = [
        (OP_IMPORT_LOT, "Импорт лота"),
        (OP_PLACE, "Размещение"),
        (OP_REMOVE, "Снятие с ячейки"),
        (OP_MOVE, "Перемещение"),
        (OP_REIMPORT_BLOCKED, "Повторный импорт заблокирован"),
        (OP_PICK, "Выдача детали"),
        (OP_CLOSE_ITEM, "Закрытие позиции"),
        (OP_CLOSE_BOX, "Закрытие коробки"),
        (OP_CLOSE_CASE, "Закрытие кейса"),
        (OP_CLOSE_CONTAINER, "Закрытие контейнера"),
        (OP_CLOSE_LOT, "Закрытие лота"),
    ]

    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_CHOICES,
        verbose_name="Тип операции",
    )

    lot = models.ForeignKey(
        WmsLot,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wms_operations",
        verbose_name="Лот",
    )

    container = models.ForeignKey(
        WmsContainer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wms_operations",
        verbose_name="Контейнер",
    )

    case = models.ForeignKey(
        WmsCase,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wms_operations",
        verbose_name="Кейс",
    )

    pallet = models.ForeignKey(
        WmsPallet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="operations",
        verbose_name="Поддон",
    )

    placement = models.ForeignKey(
        WmsPalletPlacement,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="operations",
        verbose_name="Размещение",
    )

    cell = models.ForeignKey(
        WmsStorageCell,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wms_operations",
        verbose_name="Ячейка",
    )

    message = models.TextField(blank=True, verbose_name="Описание")
    data = models.JSONField(default=dict, blank=True, verbose_name="Дополнительные данные")
    performed_by = models.CharField(max_length=150, blank=True, verbose_name="Кто выполнил")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Когда выполнено")

    class Meta:
        verbose_name = "WMS операция"
        verbose_name_plural = "WMS операции"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.get_operation_type_display()} — {self.created_at:%d.%m.%Y %H:%M:%S}"