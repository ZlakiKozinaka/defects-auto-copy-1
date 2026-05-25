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
admin.site.register(Defekty)
admin.site.register(StatusAvto)
admin.site.register(Avtomobili)
admin.site.register(PlanovyeVin)
admin.site.register(DefectPhoto)

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