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

@admin.register(WmsLot)
class WmsLotAdmin(admin.ModelAdmin):
    list_display = ("id", "lot_number", "display_name", "uploaded_by", "uploaded_at", "is_active")
    search_fields = ("lot_number", "display_name", "uploaded_by", "comment")
    list_filter = ("is_active", "uploaded_at")
    ordering = ("-uploaded_at",)


@admin.register(WmsContainer)
class WmsContainerAdmin(admin.ModelAdmin):
    list_display = ("id", "container_number", "lot", "seal_number", "existing_container")
    search_fields = ("container_number", "lot__lot_number", "seal_number")
    list_filter = ("lot",)


@admin.register(WmsCase)
class WmsCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "case_number", "container")
    search_fields = ("case_number", "container__container_number", "container__lot__lot_number")
    list_filter = ("container__lot",)


@admin.register(WmsBox)
class WmsBoxAdmin(admin.ModelAdmin):
    list_display = ("id", "box_number", "case")
    search_fields = ("box_number", "case__case_number", "case__container__container_number")
    list_filter = ("case__container__lot",)


@admin.register(WmsBoxItem)
class WmsBoxItemAdmin(admin.ModelAdmin):
    list_display = ("id", "part_number", "quantity", "unit", "box")
    search_fields = ("part_number", "chinese_name", "english_name", "box__box_number", "box__case__case_number")
    list_filter = ("unit", "box__case__container__lot")

@admin.register(WmsSite)
class WmsSiteAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)

@admin.register(WmsWarehouse)
class WmsWarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "code", "name", "is_active")
    search_fields = ("site__code", "site__name", "code", "name")
    list_filter = ("site", "is_active")


@admin.register(WmsStorageLine)
class WmsStorageLineAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "code", "name", "sort_order", "is_active")
    search_fields = ("warehouse__name", "warehouse__code", "code", "name")
    list_filter = ("warehouse", "is_active")


@admin.register(WmsStorageCell)
class WmsStorageCellAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "line", "column_number", "level_number", "capacity_units", "is_active")
    search_fields = ("line__code", "line__warehouse__code", "comment")
    list_filter = ("line__warehouse", "line", "level_number", "is_active")

    def address(self, obj):
        return obj.address


@admin.register(WmsPalletType)
class WmsPalletTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "width_units", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active", "width_units")

@admin.register(WmsStorageUnit)
class WmsStorageUnitAdmin(admin.ModelAdmin):
    list_display = ("id", "unit_type", "display_name", "lot", "is_active", "created_by", "created_at")
    search_fields = (
        "label",
        "container__container_number",
        "container__lot__lot_number",
        "case__case_number",
        "case__container__container_number",
        "box__box_number",
        "box__case__case_number",
    )
    list_filter = ("unit_type", "is_active", "created_at")

@admin.register(WmsPallet)
class WmsPalletAdmin(admin.ModelAdmin):
    list_display = ("id", "pallet_number", "pallet_type", "storage_unit", "created_by", "created_at")
    search_fields = (
        "pallet_number",
        "storage_unit__label",
        "storage_unit__container__container_number",
        "storage_unit__container__lot__lot_number",
        "storage_unit__case__case_number",
        "storage_unit__box__box_number",
        "created_by",
    )
    list_filter = ("pallet_type", "created_at")


@admin.register(WmsPalletPlacement)
class WmsPalletPlacementAdmin(admin.ModelAdmin):
    list_display = ("id", "pallet", "cell", "position_from", "position_to", "placed_by", "placed_at", "is_active")
    search_fields = ("pallet__pallet_number", "pallet__container__container_number", "cell__line__code", "placed_by", "removed_by")
    list_filter = ("is_active", "cell__line", "placed_at", "removed_at")


@admin.register(WmsOperation)
class WmsOperationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "operation_type",
        "lot",
        "container",
        "case",
        "cell",
        "performed_by",
        "created_at",
    )
    search_fields = (
        "message",
        "performed_by",
        "lot__lot_number",
        "container__container_number",
        "case__case_number",
        "cell__line__code",
    )
    list_filter = (
        "operation_type",
        "created_at",
        "cell__line",
    )
    readonly_fields = (
        "operation_type",
        "lot",
        "container",
        "case",
        "pallet",
        "placement",
        "cell",
        "message",
        "data",
        "performed_by",
        "created_at",
    )