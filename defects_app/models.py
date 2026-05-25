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