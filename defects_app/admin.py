from django.contrib import admin
from .models import *

admin.site.register(Modeli)
admin.site.register(Smeny)
admin.site.register(Mesta)
admin.site.register(Tipy)
admin.site.register(Oblasti)
admin.site.register(Greydy)
admin.site.register(Otvetstvennye)
admin.site.register(Stancii)
admin.site.register(StatusAvto)
admin.site.register(DefectPhoto)


@admin.register(Avtomobili)
class AvtomobiliAdmin(admin.ModelAdmin):
    list_display = (
        "vin",
        "model",
        "data_sozdaniya",
        "kto_sozdal",
        "dvs",
        "perednij_dvigatel",
        "zadnij_dvigatel",
        "batareya",
    )
    search_fields = (
        "vin",
        "model__nazvanie",
        "station1_sequence_number",
        "kto_sozdal",
        "telematika",
        "glonass",
        "glonass_sn",
        "glonass_imei",
        "glonass_iccid",
        "dvs",
        "perednij_dvigatel",
        "zadnij_dvigatel",
        "batareya",
    )
    list_filter = (
        "model",
        "created_on_station_1",
        "proshla_bestenevaya",
        "data_sozdaniya",
    )
    ordering = ("-data_sozdaniya",)


@admin.register(Defekty)
class DefektyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "avto",
        "data",
        "smena",
        "mesto",
        "tip",
        "oblast",
        "greyd",
        "otvetstvennyj",
        "stanciya",
        "ustraneno",
        "proveren",
        "kto_sozdal",
    )
    search_fields = (
        "avto__vin",
        "kommentarij",
        "kto_sozdal",
        "kto_ustranil",
        "kto_razreshil",
        "tip__nazvanie",
        "oblast__nazvanie",
        "mesto__nazvanie",
        "stanciya__nazvanie",
        "otvetstvennyj__nazvanie",
    )
    list_filter = (
        "smena",
        "mesto",
        "tip",
        "oblast",
        "greyd",
        "otvetstvennyj",
        "stanciya",
        "ustraneno",
        "proveren",
        "data",
    )
    ordering = ("-data",)


@admin.register(PlanovyeVin)
class PlanovyeVinAdmin(admin.ModelAdmin):
    list_display = (
        "vin",
        "model",
        "nomer_partii",
        "nomer_lota",
        "cvet_kuzova",
        "cvet_salona",
        "komplektaciya",
        "otts",
        "kto_zagruzil",
        "data_zagruzki",
    )
    search_fields = (
        "vin",
        "model",
        "nomer_partii",
        "nomer_lota",
        "cvet_kuzova",
        "cvet_salona",
        "komplektaciya",
        "otts",
        "file_name",
        "kto_zagruzil",
    )
    list_filter = (
        "model",
        "nomer_partii",
        "nomer_lota",
        "data_zagruzki",
    )
    ordering = ("-data_zagruzki",)

@admin.register(StationOnePrintBufferEntry)
class StationOnePrintBufferEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "car",
        "added_at",
        "printed_at",
    )
    search_fields = (
        "car__vin",
        "car__station1_sequence_number",
    )
    list_filter = (
        "printed_at",
        "added_at",
    )
    ordering = ("-added_at",)

@admin.register(DailyProductionPlan)
class DailyProductionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "plan_count",
        "created_by",
        "updated_by",
        "updated_at",
    )
    list_filter = ("date",)
    ordering = ("-date",)

@admin.register(DefectApprovalForSgp)
class DefectApprovalForSgpAdmin(admin.ModelAdmin):
    list_display = (
        "avto",
        "defect",
        "approved_by",
        "approved_at",
    )

    search_fields = (
        "avto__vin",
        "approved_by",
        "comment",
    )

    list_filter = (
        "approved_at",
    )

    readonly_fields = (
        "defect",
        "avto",
        "approved_by",
        "approved_at",
        "comment",
    )

@admin.register(VinPrefix)
class VinPrefixAdmin(admin.ModelAdmin):
    list_display = (
        "model",
        "prefix",
        "is_active",
        "comment",
    )
    list_filter = (
        "model",
        "is_active",
    )
    search_fields = (
        "model__nazvanie",
        "prefix",
        "comment",
    )

class ContainerSealInline(admin.TabularInline):
    model = ContainerSeal
    extra = 1


class ContainerReceiptPhotoInline(admin.TabularInline):
    model = ContainerReceiptPhoto
    extra = 1

class ContainerCarInline(admin.TabularInline):
    model = ContainerCar
    extra = 0
    readonly_fields = (
        "avto",
        "accepted_by",
        "accepted_at",
        "comment",
    )

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "is_active",
    )
    search_fields = (
        "number",
    )


@admin.register(ContainerReceipt)
class ContainerReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "daily_number",
        "receipt_date",
        "container",
        "vehicle_number",
        "created_by",
        "created_at",
    )

    search_fields = (
        "container__number",
        "vehicle_number",
        "components_name",
    )

    list_filter = (
        "receipt_date",
        "created_at",
    )

    inlines = [
        ContainerSealInline,
        ContainerReceiptPhotoInline,
        ContainerCarInline,
    ]

@admin.register(ContainerCar)
class ContainerCarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "receipt",
        "avto",
        "accepted_by",
        "accepted_at",
    )

    search_fields = (
        "avto__vin",
        "receipt__container__number",
        "accepted_by",
    )

    list_filter = (
        "accepted_at",
    )